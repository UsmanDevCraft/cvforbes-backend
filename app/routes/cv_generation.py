from time import perf_counter
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import ALLOWED_CONTENT_TYPES, MAX_FILE_SIZE, MAX_TEXT_LENGTH
from app.core.abuse_points import AI_FAILURE
from app.schemas.tailored_cv import FinalTailoredOutput
from app.services.abuse_service import AbuseService
from app.services.anonymous_user_service import AnonymousUserService
from app.services.cv_generator import (
    GenerationResult,
    cleanup_extracted_text,
    generate_tailored_assets,
)
from app.services.generation_service import GenerationService
from app.utils.logger import logger
from app.utils.pdf import extract_text_from_pdf

router = APIRouter(tags=["CV Generation"])

limiter = Limiter(key_func=get_remote_address)

anonymous_service = AnonymousUserService()
generation_service = GenerationService()
abuse_service = AbuseService()


@router.post("/api/v1/tailor-cv", response_model=FinalTailoredOutput)
@limiter.limit("3/minute")  # Strict action: Max 3 hits per minute per IP
async def tailor_cv_endpoint(
    request: Request,
    job_description: Annotated[
        str,
        Form(
            min_length=10,
        ),
    ],
    cv_file: UploadFile = File(...),
):
    # Normalize CRLF (\r\n) to LF (\n) to match frontend counting logic
    normalized_job_desc = job_description.replace("\r\n", "\n")

    # Perform the character length check manually
    if len(normalized_job_desc) > 3500:
        raise HTTPException(
            status_code=422, detail="Job description must be 3500 characters or fewer."
        )

    # Validate file extension
    if not cv_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Validate MIME type
    if cv_file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    # Step 1: Read and Extract Text
    file_bytes = await cv_file.read()

    # Reject empty files
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Reject files larger than 5 MB
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, detail="Maximum allowed file size is 5 MB."
        )

    raw_cv_text = extract_text_from_pdf(file_bytes)

    # Clean and sanitize extracted resume text
    raw_cv_text = cleanup_extracted_text(raw_cv_text)

    # Reject PDFs with no readable text
    if not raw_cv_text:
        raise HTTPException(
            status_code=400, detail="The uploaded PDF contains no readable text."
        )

    # Reject excessively large resumes
    if len(raw_cv_text) > MAX_TEXT_LENGTH:
        raise HTTPException(status_code=400, detail="Resume contains too much text.")

    # Step 2 & 3: Invoke LangChain Engine to compare, rewrite, and parse JSON
    try:
        logger.info(
            f"Processing resume | Size={len(file_bytes)} bytes | Characters={len(raw_cv_text)}"
        )

        start = perf_counter()

        # CRITICAL RENDER FIX:
        # Run the heavy LangChain blocking function in an external thread pool.
        # This keeps FastAPI's main loop awake so Render doesn't think the app crashed/timed out.
        result: GenerationResult = await run_in_threadpool(
            generate_tailored_assets, raw_cv_text, normalized_job_desc
        )
        final_output = result.output

        generation_time_ms = int((perf_counter() - start) * 1000)

        await anonymous_service.increment_usage(request.state.anonymous_user)

        await generation_service.save_generation(
            anonymous_user=request.state.anonymous_user,
            filename=cv_file.filename,
            provider=result.provider,
            model=result.model,
            generation_time_ms=generation_time_ms,
            ats_score=final_output.analytics.ats_score,
            parse_score=final_output.analytics.resume_parse_rate,
            parsed_resume=result.parsed_profile.model_dump(),
            tailored_resume=final_output.cv.model_dump(),
            cover_letter=final_output.cover_letter,
        )

        logger.info(
            "Resume processed successfully.",
            extra={
                "fingerprint": request.state.anonymous_user.fingerprint,
                "requests_today": request.state.anonymous_user.requests_today + 1,
            },
        )

        return final_output

    except HTTPException:
        raise

    except Exception:
        await abuse_service.increase_score(
            user=request.state.anonymous_user,
            identity=request.state.identity,
            points=AI_FAILURE,
            reason="Unexpected AI processing failure",
        )

        logger.exception("Unexpected error while processing resume.")

        raise HTTPException(
            status_code=500,
            detail="Unexpected AI processing error. Please try again later.",
        )
