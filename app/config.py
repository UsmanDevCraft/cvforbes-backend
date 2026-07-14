from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")

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
