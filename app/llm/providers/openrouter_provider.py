from app.config import OPENROUTER_API_KEY
from langchain_openai import ChatOpenAI

from app.llm.base import BaseProvider
from app.llm.models import Models


class OpenRouterProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "openrouter"

    @property
    def model_name(self) -> str:
        return Models.OPENROUTER_DEEPSEEK

    @property
    def rpm_limit(self) -> int:
        return 20

    def __init__(self):
        self._model = ChatOpenAI(
            model=Models.OPENROUTER_DEEPSEEK,
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.3,
            timeout=60,
            default_headers={
                "HTTP-Referer": "https://cvforbes.vercel.app",
                "X-Title": "CVForbes",
            },
        )

    def get_model(self):
        return self._model
