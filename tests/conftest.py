import os
import pytest

pytest_plugins = ["tests.fixtures.pdf_fixtures", "tests.fixtures.profile_fixtures"]

# Set mock environment variables before any application code is imported
os.environ["GOOGLE_API_KEY"] = "mock-google-key"
os.environ["GROQ_API_KEY"] = "mock-groq-key"
os.environ["OPENROUTER_API_KEY"] = "mock-openrouter-key"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

from fastapi.testclient import TestClient
from app.main import app


def pytest_addoption(parser):
    """Register custom command-line arguments for pytest."""
    parser.addoption(
        "--pdf-path",
        action="store",
        default=None,
        help="Absolute or relative path to a live PDF file to run tests against",
    )


@pytest.fixture
def live_pdf_bytes(request):
    """Fixture that reads raw bytes of the user-provided live PDF path, if specified."""
    pdf_path = request.config.getoption("--pdf-path")
    if not pdf_path:
        return None

    abs_path = os.path.abspath(pdf_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Provided live PDF file does not exist at: {abs_path}")

    with open(abs_path, "rb") as f:
        return f.read()


@pytest.fixture
def client() -> TestClient:
    """Fixture for FastAPI TestClient."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Autouse fixture to reset the slowapi rate limiter between tests to ensure isolation."""
    from app.main import limiter

    limiter.reset()
