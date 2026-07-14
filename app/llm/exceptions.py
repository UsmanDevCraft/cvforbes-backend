class ProviderError(Exception):
    """Base provider exception."""


class ProviderRateLimitError(ProviderError):
    """Provider exceeded RPM."""


class ProviderTimeoutError(ProviderError):
    """Provider timed out."""


class ProviderUnavailableError(ProviderError):
    """Provider temporarily unavailable."""


class AllProvidersFailedError(ProviderError):
    """No provider was able to complete the request."""
