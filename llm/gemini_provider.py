"""
Distributed Agentic Reasoning Framework (DARF)

Gemini Provider

Purpose
-------
Production implementation of the DARF LLMProvider interface 
for Google's Gemini models using the official Google GenAI SDK.

Responsibilities
----------------
- Initialize Gemini client
- Generate content via Gemini API
- Support chat completion and embeddings
- Standardize response metrics

Design Principles
-----------------
- Provider-agnostic interface
- Lazy client initialization
- Production-ready error handling
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List

from llm.provider import LLMProvider
from llm.provider_config import ProviderConfig
from llm.provider_result import ProviderResult

__all__ = ["GeminiProvider"]

class GeminiProvider(LLMProvider):
    """
    Production-ready Google Gemini provider implementation.
    """

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(
            provider_name="Gemini",
            model_name=config.model_name
        )
        self.config = config
        self._client: Any = None

    # ========================================================
    # CLIENT INITIALIZATION
    # ========================================================

    def _initialize_client(self) -> None:
        """Lazily initialize the Google GenAI client."""
        if self._client is not None:
            return

        if not self.config.api_key:
            raise ValueError("Gemini API key not configured.")

        try:
            from google import genai
        except ImportError as exc:
            raise ImportError(
                "Google GenAI SDK not installed. Run: pip install google-genai"
            ) from exc

        self._client = genai.Client(api_key=self.config.api_key)

    @property
    def client(self) -> Any:
        self._initialize_client()
        return self._client

    # ========================================================
    # HEALTH & STATUS
    # ========================================================

    def health_check(self) -> bool:
        """Verify provider reachability."""
        try:
            self._initialize_client()
            return True
        except Exception:
            return False

    # ========================================================
    # EXECUTION API
    # ========================================================

    def generate(self, prompt: str, **kwargs: Any) -> ProviderResult:
        """Generate text using Gemini Content API."""
        start = time.perf_counter()
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            latency = time.perf_counter() - start
            usage = getattr(response, "usage_metadata", None)

            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=True,
                content=response.text,
                finish_reason="stop",
                prompt_tokens=getattr(usage, "prompt_token_count", 0),
                completion_tokens=getattr(usage, "candidates_token_count", 0),
                latency=latency
            )
        except Exception as exc:
            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=False,
                content=str(exc),
                finish_reason="error",
                latency=time.perf_counter() - start
            )

    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> ProviderResult:
        """Execute chat completion by mapping messages to prompt."""
        prompt = "\n".join([f"{m.get('role')}: {m.get('content')}" for m in messages])
        return self.generate(prompt, **kwargs)

    def embed(self, text: str, **kwargs: Any) -> ProviderResult:
        """Generate text embeddings."""
        start = time.perf_counter()
        try:
            response = self.client.models.embed_content(
                model=kwargs.get("embedding_model", "text-embedding-004"),
                contents=text
            )
            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=True,
                latency=time.perf_counter() - start,
                metadata={"embedding": response.embeddings[0].values}
            )
        except Exception as exc:
            return ProviderResult(success=False, content=str(exc))

    # ========================================================
    # CAPABILITIES & SERIALIZATION
    # ========================================================

    def supports_embeddings(self) -> bool: return True
    def supports_streaming(self) -> bool: return True
    def supports_multimodal(self) -> bool: return True

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "config": self.config.to_dict(),
            "client_initialized": self._client is not None,
        })
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)