import logging
import re

import fitz
from fastapi import HTTPException

from app.config import MAX_PDF_PAGES

logger = logging.getLogger(__name__)


def _normalize_text(text: str) -> str:
    """
    Normalize extracted PDF text while preserving resume structure.
    """
    text = text.replace("\x00", "")

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove trailing whitespace
    text = "\n".join(line.rstrip() for line in text.splitlines())

    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract readable text from a PDF resume using PyMuPDF.

    This function intentionally performs only one extraction strategy.
    Resume structure reconstruction is delegated to the LLM parser.
    """

    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
            if pdf.page_count > MAX_PDF_PAGES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Resume exceeds the maximum limit of {MAX_PDF_PAGES} pages.",
                )

            pages = []

            for page in pdf:
                # sort=True usually produces a better reading order
                page_text = page.get_text("text", sort=True)

                if page_text:
                    pages.append(page_text)

            extracted_text = _normalize_text("\n".join(pages))

            if not extracted_text:
                raise HTTPException(
                    status_code=400,
                    detail="No readable text found in the uploaded PDF.",
                )

            logger.info(
                "PDF extraction successful | pages=%d chars=%d words=%d",
                pdf.page_count,
                len(extracted_text),
                len(extracted_text.split()),
            )

            return extracted_text

    except HTTPException:
        raise

    except Exception:
        logger.exception("Failed to extract PDF text.")

        raise HTTPException(
            status_code=400,
            detail="Failed to read the uploaded PDF.",
        )


def generate_pdf(text: str) -> bytes:
    """
    Generate a simple PDF from text using PyMuPDF (fitz) and return bytes.
    """
    try:
        doc = fitz.open()
        page = doc.new_page()
        # Insert text with a basic margin
        page.insert_text((72, 72), text)
        pdf_bytes = doc.write()
        doc.close()
        return pdf_bytes
    except Exception:
        logger.exception("Failed to generate PDF.")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate PDF.",
        )
