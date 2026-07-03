"""
Distributed Agentic Reasoning Framework (DARF)

Azure OpenAI Provider

Purpose
-------
Production implementation of the DARF LLMProvider interface 
for Azure OpenAI Service.

Responsibilities
----------------
- Initialize Azure-specific OpenAI client
- Generate text, chat, and embeddings
- Handle Azure authentication and endpoint routing

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import time
import json
from typing import Any, Dict, List

from llm.provider import LLMProvider
from llm.provider_config import ProviderConfig
from llm.provider_result import ProviderResult

__all__ = ["AzureOpenAIProvider"]

class AzureOpenAIProvider(LLMProvider):
    """
    Production-ready Azure OpenAI provider implementation.
    """

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(
            provider_name="AzureOpenAI",
            model_name=config.model_name
        )
        self.config = config
        self._client: Any = None

    # ========================================================
    # CLIENT INITIALIZATION
    # ========================================================

    def _initialize_client(self) -> None:
        """Lazily initialize the Azure OpenAI client."""
        if self._client is not None:
            return

        # Institutional validation for Azure requirements
        if not self.config.api_key:
            raise ValueError("Azure OpenAI API key not configured.")
        if not self.config.base_url:
            raise ValueError("Azure endpoint (base_url) not configured.")
        if not self.config.api_version:
            raise ValueError("Azure API version not configured.")

        try:
            from openai import AzureOpenAI
        except ImportError as exc:
            raise ImportError(
                "OpenAI SDK not installed. Run: pip install openai"
            ) from exc

        self._client = AzureOpenAI(
            api_key=self.config.api_key,
            api_version=self.config.api_version,
            azure_endpoint=self.config.base_url,
        )

    def client(self) -> Any:
        self._initialize_client()
        return self._client

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    def health_check(self) -> bool:
        """Verify Azure OpenAI availability."""
        try:
            self.client()
            return True
        except Exception:
            return False

    # ========================================================
    # EXECUTION API
    # ========================================================

    def generate(self, prompt: str, **kwargs: Any) -> ProviderResult:
        """Generate text using Azure OpenAI."""
        start = time.perf_counter()
        try:
            response = self.client().chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens)
            )
            
            latency = time.perf_counter() - start
            usage = response.usage
            
            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=True,
                content=response.choices[0].message.content,
                finish_reason=response.choices[0].finish_reason,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                latency=latency
            )
        except Exception as exc:
            return ProviderResult(
                success=False,
                content=str(exc),
                finish_reason="error",
                latency=time.perf_counter() - start
            )

    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> ProviderResult:
        """Execute chat completion."""
        start = time.perf_counter()
        try:
            response = self.client().chat.completions.create(
                model=self.model_name,
                messages=messages,
                **kwargs
            )
            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=True,
                content=response.choices[0].message.content,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                latency=time.perf_counter() - start
            )
        except Exception as exc:
            return ProviderResult(success=False, content=str(exc))

    def embed(self, text: str, **kwargs: Any) -> ProviderResult:
        """Generate embeddings."""
        try:
            response = self.client().embeddings.create(
                input=text, 
                model=kwargs.get("embedding_model", self.model_name)
            )
            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=True,
                metadata={"embedding": response.data[0].embedding}
            )
        except Exception as exc:
            return ProviderResult(success=False, content=str(exc))

    # ========================================================
    # SERIALIZATION & LIFECYCLE
    # ========================================================

    def reset(self) -> None:
        self._client = None
        self.metadata.clear()

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({"config": self.config.to_dict(), "client_initialized": self._client is not None})
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)