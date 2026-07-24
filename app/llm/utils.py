from app.utils.logger import logger


def log_provider(provider: str, model: str):
    logger.info(f"LLM Provider={provider} | Model={model}")


def log_provider_failure(provider: str, error: Exception):
    logger.warning(f"LLM Provider={provider} failed | {error}")
