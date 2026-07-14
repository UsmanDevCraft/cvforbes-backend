from app.config import OLLAMA_BASE_URL
from langchain_ollama import ChatOllama

from app.llm.base import BaseProvider
from app.llm.models import Models


class OllamaProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return Models.OLLAMA_LLAMA

    @property
    def rpm_limit(self) -> int:
        return 1000

    def __init__(self):
        self._model = ChatOllama(
            model=Models.OLLAMA_LLAMA,
            base_url=OLLAMA_BASE_URL,
            temperature=0.3,
        )

    def get_model(self):
        return self._model
