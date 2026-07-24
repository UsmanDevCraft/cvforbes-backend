from enum import Enum


class StrEnum(str, Enum):
    pass


class Models(StrEnum):
    # Groq
    GROQ_LLAMA = "llama-3.3-70b-versatile"

    # OpenRouter
    OPENROUTER_DEEPSEEK = "deepseek/deepseek-chat-v3-0324"

    # Gemini
    GEMINI_FLASH = "gemini-3.5-flash"
