from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import (
    run_in_threadpool,
)
from typing import Annotated
from app.services.cv_generator import generate_tailored_assets, cleanup_extracted_text
from app.schemas.tailored_cv import FinalTailoredOutput
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import (
    MAX_FILE_SIZE,
    MAX_TEXT_LENGTH,
    ALLOWED_CONTENT_TYPES,
)
from app.utils.logger import logger
from app.utils.pdf import extract_text_from_pdf
from dotenv import load_dotenv

load_dotenv()

# Initialize the limiter (tracks users by their IP address)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="AI CV Tailor Engine API")

# Add the rate limit error handler to FastAPI
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# ────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://cvforbes.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/tailor-cv", response_model=FinalTailoredOutput)
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

        # CRITICAL RENDER FIX:
        # Run the heavy LangChain blocking function in an external thread pool.
        # This keeps FastAPI's main loop awake so Render doesn't think the app crashed/timed out.
        final_output = await run_in_threadpool(
            generate_tailored_assets, raw_cv_text, normalized_job_desc
        )

        logger.info("Resume processed successfully.")

        return final_output

    except HTTPException:
        raise

    except Exception:
        logger.exception("Unexpected error while processing resume.")

        raise HTTPException(
            status_code=500,
            detail="Unexpected AI processing error. Please try again later.",
        )
