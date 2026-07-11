from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import pypdf
import io
from app.services.cv_generator import generate_tailored_assets
from app.schemas.tailored_cv import FinalTailoredOutput
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

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
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF document: {str(e)}")

@app.post("/api/tailor-cv", response_model=FinalTailoredOutput)
@limiter.limit("5/minute") # Strict action: Max 5 hits per minute per IP
async def tailor_cv_endpoint(
    request: Request,
    cv_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    # Ensure uploaded file is a PDF
    if not cv_file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF file format is supported at this moment.")
        
    # Step 1: Read and Extract Text
    file_bytes = await cv_file.read()
    raw_cv_text = extract_text_from_pdf(file_bytes)
    
    if not raw_cv_text:
         raise HTTPException(status_code=400, detail="The uploaded PDF file is empty or unreadable.")
         
    # Step 2 & 3: Invoke LangChain Engine to compare, rewrite, and parse JSON
    try:
        final_output = generate_tailored_assets(raw_cv_text, job_description)
        return final_output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing engine error: {str(e)}")