from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import pypdf
import io
from typing import Annotated
from app.services.cv_generator import generate_tailored_assets
from app.schemas.tailored_cv import FinalTailoredOutput
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import (
    MAX_FILE_SIZE,
    MAX_PDF_PAGES,
    ALLOWED_CONTENT_TYPES,
)

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

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_file)

        # Reject encrypted PDFs
        if reader.is_encrypted:
            raise HTTPException(
                status_code=400,
                detail="Encrypted PDF files are not supported."
            )

        # Limit PDF pages
        if len(reader.pages) > MAX_PDF_PAGES:
            raise HTTPException(
                status_code=400,
                detail=f"Resume exceeds the maximum limit of {MAX_PDF_PAGES} pages."
            )

        extracted_text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                extracted_text += page_text + "\n"

        return extracted_text.strip()

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Failed to read the uploaded PDF."
        )

@app.post("/api/tailor-cv", response_model=FinalTailoredOutput)
@limiter.limit("5/minute") # Strict action: Max 5 hits per minute per IP
async def tailor_cv_endpoint(
    request: Request,
    cv_file: UploadFile = File(...),
    job_description: Annotated[
    str,
    Form(
        min_length=10,
        max_length=2500,
    ),
]
):

    # Validate file extension
    if not cv_file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # Validate MIME type
    if cv_file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type."
        )
        
    # Step 1: Read and Extract Text
    file_bytes = await cv_file.read()

    # Reject empty files
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    # Reject files larger than 5 MB
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Maximum allowed file size is 5 MB."
        )

    raw_cv_text = extract_text_from_pdf(file_bytes)
    
    if not raw_cv_text:
         raise HTTPException(status_code=400, detail="The uploaded PDF file is empty or unreadable.")
         
    # Step 2 & 3: Invoke LangChain Engine to compare, rewrite, and parse JSON
    try:
        final_output = generate_tailored_assets(raw_cv_text, job_description)
        return final_output
        