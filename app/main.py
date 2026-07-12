from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from app.services.cv_generator import generate_tailored_assets
from app.schemas.tailored_cv import FinalTailoredOutput
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import re
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
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/tailor-cv", response_model=FinalTailoredOutput)
@limiter.limit("5/minute")  # Strict action: Max 5 hits per minute per IP
async def tailor_cv_endpoint(
    request: Request,
    job_description: Annotated[
        str,
        Form(
            min_length=10,
            max_length=2500,
        ),
    ],
    cv_file: UploadFile = File(...),
):

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

    # Normalize whitespace
    raw_cv_text = re.sub(r"\s+", " ", raw_cv_text).strip()

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

        final_output = generate_tailored_assets(raw_cv_text, job_description)

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
