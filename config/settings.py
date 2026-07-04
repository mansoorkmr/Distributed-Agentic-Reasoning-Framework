"""
Global application settings.

Loads environment variables and provides
a single configuration object for DARF.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


# Load .env automatically
load_dotenv()


@dataclass(slots=True)
class Settings:
    """
    Global DARF configuration.
    """

    provider: str = os.getenv(
        "LLM_PROVIDER",
        "openai",
    )

    model: str = os.getenv(
        "LLM_MODEL",
        "gpt-5",
    )

    api_key: str | None = os.getenv(
        "OPENAI_API_KEY",
    )

    base_url: str | None = os.getenv(
        "OPENAI_BASE_URL",
    )

    ollama_base_url: str = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434",
    )

    temperature: float = float(
        os.getenv(
            "LLM_TEMPERATURE",
            "0.7",
        )
    )

    max_tokens: int = int(
        os.getenv(
            "LLM_MAX_TOKENS",
            "4096",
        )
    )


settings = Settings()