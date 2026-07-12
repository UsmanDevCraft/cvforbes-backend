import io

import pypdf
from fastapi import HTTPException

from app.config import MAX_PDF_PAGES


def extract_text_from_pdf(file_bytes: bytes) -> str:

    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_file)

        # Reject encrypted PDFs
        if reader.is_encrypted:
            raise HTTPException(
                status_code=400, detail="Encrypted PDF files are not supported."
            )

        # Reject very large resumes
        if len(reader.pages) > MAX_PDF_PAGES:
            raise HTTPException(
                status_code=400,
                detail=f"Resume exceeds the maximum limit of {MAX_PDF_PAGES} pages.",
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
        raise HTTPException(status_code=400, detail="Failed to read the uploaded PDF.")
