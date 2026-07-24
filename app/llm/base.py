from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel


class BaseProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider name."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the underlying LLM model."""

    @property
    @abstractmethod
    def rpm_limit(self) -> int:
        """Maximum requests per minute."""

    @abstractmethod
    def get_model(self) -> BaseChatModel:
        """Return the LangChain chat model."""

    def get_structured_model(
        self,
        schema: type[BaseModel],
    ):
        return self.get_model().with_structured_output(schema)
