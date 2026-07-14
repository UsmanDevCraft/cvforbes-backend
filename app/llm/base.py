from abc import ABC, abstractmethod
from typing import Type

from pydantic import BaseModel
from langchain_core.language_models import BaseChatModel


class BaseProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider name."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @property
    @abstractmethod
    def rpm_limit(self) -> int:
        """Maximum requests per minute."""
        pass

    @abstractmethod
    def get_model(self) -> BaseChatModel:
        """Return the LangChain chat model."""
        pass

    def get_structured_model(
        self,
        schema: Type[BaseModel],
    ):

        return self.get_model().with_structured_output(schema)
