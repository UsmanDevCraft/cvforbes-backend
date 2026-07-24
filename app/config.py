import os

from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Maximum upload size (5 MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

# Maximum number of pages allowed in a resume
MAX_PDF_PAGES = 10

# Maximum extracted text length
MAX_TEXT_LENGTH = 30000

# Allowed PDF MIME types
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
}

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

ALLOWED_ADMIN_EMAILS = [
    email.strip()
    for email in os.getenv("ALLOWED_ADMIN_EMAILS", "").split(",")
    if email.strip()
]

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
