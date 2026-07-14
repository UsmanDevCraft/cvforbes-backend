from app.config import GOOGLE_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI

from app.llm.base import BaseProvider
from app.llm.models import Models


class GeminiProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return Models.GEMINI_FLASH

    @property
    def rpm_limit(self) -> int:
        return 6

    def __init__(self):
        self._model = ChatGoogleGenerativeAI(
            model=Models.GEMINI_FLASH,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.3,
            timeout=60,
        )

    def get_model(self):
        return self._model
