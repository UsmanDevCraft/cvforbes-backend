from app.config import GROQ_API_KEY
from langchain_groq import ChatGroq

from app.llm.base import BaseProvider
from app.llm.models import Models


class GroqProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "groq"

    @property
    def model_name(self) -> str:
        return Models.GROQ_LLAMA

    @property
    def rpm_limit(self) -> int:
        # Adjust based on your current Groq tier
        return 30

    def __init__(self):
        self._model = ChatGroq(
            model=Models.GROQ_LLAMA,
            api_key=GROQ_API_KEY,
            temperature=0.3,
            timeout=60,
        )

    def get_model(self):
        return self._model
