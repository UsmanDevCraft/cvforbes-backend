from typing import Type

from pydantic import BaseModel

from app.llm.exceptions import (
    AllProvidersFailedError,
)
from app.llm.provider_state import ProviderState
from app.llm.providers import (
    GeminiProvider,
    GroqProvider,
    OllamaProvider,
    OpenRouterProvider,
)
from app.llm.utils import (
    log_provider,
    log_provider_failure,
)


class LLMRouter:
    COOLDOWN_SECONDS = 60

    def __init__(self):

        self.providers = [
            GroqProvider(),
            OpenRouterProvider(),
            OllamaProvider(),
            GeminiProvider(),
        ]

        self.states = {provider.name: ProviderState() for provider in self.providers}

    def _can_use(self, provider):

        state = self.states[provider.name]

        state.reset_if_needed()

        if state.is_in_cooldown:
            return False

        if state.requests >= provider.rpm_limit:
            return False

        return True

    def invoke(
        self,
        prompt,
    ):

        last_error = None

        for provider in self.providers:
            state = self.states[provider.name]

            if not self._can_use(provider):
                continue

            model = provider.get_model()

            try:
                response = model.invoke(prompt)

            except Exception as e:
                last_error = e

                state.set_cooldown(self.COOLDOWN_SECONDS)

                log_provider_failure(
                    provider.name,
                    e,
                )

                continue

            state.increment()

            log_provider(
                provider.name,
                provider.model_name,
            )

            return response

        raise AllProvidersFailedError(str(last_error))

    def invoke_structured(
        self,
        prompt,
        schema: Type[BaseModel],
    ):

        last_error = None

        for provider in self.providers:
            state = self.states[provider.name]

            if not self._can_use(provider):
                continue

            model = provider.get_structured_model(schema)

            try:
                response = model.invoke(prompt)

            except Exception as e:
                last_error = e

                state.set_cooldown(self.COOLDOWN_SECONDS)

                log_provider_failure(
                    provider.name,
                    e,
                )

                continue

            state.increment()

            log_provider(
                provider.name,
                provider.model_name,
            )

            return response

        raise AllProvidersFailedError(str(last_error))
