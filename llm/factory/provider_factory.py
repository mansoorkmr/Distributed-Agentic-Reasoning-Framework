"""
Distributed Agentic Reasoning Framework (DARF)

Provider Factory

Purpose
-------
Centralized factory for creating concrete implementations of LLMProvider 
based on the application configuration settings.

Design Principles
-----------------
- Single Responsibility Principle (SRP)
- Strict type tracking via static analysis
- Dynamic lookup execution pattern (Strict Lazy Imports)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# Only import the global settings at the top level
from config import settings

if TYPE_CHECKING:
    from llm.provider import LLMProvider

__all__ = ["ProviderFactory"]


class ProviderFactory:
    """
    Factory responsible for constructing the configured LLM provider.
    """

    @staticmethod
    def create() -> LLMProvider:
        """
        Builds and resolves an LLMProvider instance dynamically matching 
        the system configurations.

        Returns
        -------
        LLMProvider
            An initialized concrete provider instance.

        Raises
        ------
        ValueError
            If the configured provider name is unsupported or unknown.
        """
        # ========================================================
        # STRICT LAZY IMPORTS (Guarantees no circular dependencies)
        # ========================================================
        from llm.provider_config import ProviderConfig

        provider_target = settings.provider.lower().strip()

        base_url = settings.base_url
        
        # Dynamically map local endpoints for specific providers
        if provider_target == "ollama":
            base_url = getattr(settings, "ollama_base_url", "http://localhost:11434")

        # Package runtime attributes into standardized configuration data contract
        config = ProviderConfig(
            provider_name=settings.provider,
            model_name=settings.model,
            api_key=settings.api_key,
            base_url=base_url,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )

        # Inject Azure specific properties safely if present in settings schema
        if hasattr(settings, "api_version") and settings.api_version:
            config.api_version = settings.api_version

        # ========================================================
        # LAZY ROUTING
        # ========================================================
        if provider_target == "openai":
            from llm.openai_provider import OpenAIProvider
            return OpenAIProvider(config)

        if provider_target == "gemini":
            from llm.gemini_provider import GeminiProvider
            return GeminiProvider(config)

        if provider_target == "ollama":
            from llm.ollama_provider import OllamaProvider
            return OllamaProvider(config)

        if provider_target == "huggingface":
            from llm.huggingface_provider import HuggingFaceProvider
            return HuggingFaceProvider(config)

        if provider_target in ("azure", "azure_openai", "azureopenai"):
            from llm.azure_openai_provider import AzureOpenAIProvider
            return AzureOpenAIProvider(config)

        if provider_target == "llama_cpp":
            from llm.llama_cpp_provider import LlamaCppProvider
            return LlamaCppProvider(config)

        raise ValueError(
            f"Unsupported or unknown LLM provider sequence configured: '{settings.provider}'"
        )