import pytest
import fitz


@pytest.fixture
def valid_pdf() -> bytes:
    """Fixture returning valid PDF bytes with selectable text."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (72, 72),
        (
            "John Doe\n"
            "Email: john@example.com\n"
            "Phone: 123-456-7890\n"
            "Professional Summary:\n"
            "Experienced Software Engineer.\n"
            "Experience:\n"
            "Company A - Software Developer (June 2021 - Present)\n"
            "- Developed a cool app.\n"
            "Skills:\n"
            "Python, FastAPI, Docker\n"
            "Education:\n"
            "University X - BS Computer Science (2016 - 2020)"
        ),
    )
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


@pytest.fixture
def empty_pdf() -> bytes:
    """Fixture returning PDF bytes with no text (blank page)."""
    doc = fitz.open()
    doc.new_page()
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


@pytest.fixture
def corrupted_pdf() -> bytes:
    """Fixture returning corrupted PDF bytes."""
    return b"%PDF-1.4\n%corrupted_data\nEOF"


@pytest.fixture
def image_only_pdf() -> bytes:
    """Fixture returning PDF bytes containing only a drawn shape/image, no text."""
    doc = fitz.open()
    page = doc.new_page()
    # Draw a rectangle to act as an image shape
    page.draw_rect(fitz.Rect(100, 100, 200, 200), color=(1, 0, 0), fill=(0, 1, 0))
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


@pytest.fixture
def duplicate_content_pdf() -> bytes:
    """Fixture returning PDF bytes with duplicate sections."""
    doc = fitz.open()
    page1 = doc.new_page()
    page1.insert_text(
        (72, 72),
        "John Doe\nExperience:\nSoftware Engineer at Company A\nSoftware Engineer at Company A",
    )
    page2 = doc.new_page()
    page2.insert_text(
        (72, 72),
        "John Doe\nExperience:\nSoftware Engineer at Company A\nSoftware Engineer at Company A",
    )
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes
