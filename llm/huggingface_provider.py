"""
Distributed Agentic Reasoning Framework (DARF)

Hugging Face Provider

Purpose
-------
Production implementation of the DARF LLMProvider interface
using the Hugging Face Inference API.

Responsibilities
----------------
- Initialize Hugging Face InferenceClient
- Generate text, chat completions, and embeddings
- Standardize response metrics

Design Principles
-----------------
- Provider-agnostic interface
- Lazy client initialization
- Production-ready error handling
"""

from __future__ import annotations

import time
import json
from typing import Any, Dict, List, Optional

from llm.provider import LLMProvider
from llm.provider_config import ProviderConfig
from llm.provider_result import ProviderResult

__all__ = ["HuggingFaceProvider"]

class HuggingFaceProvider(LLMProvider):
    """
    Hugging Face Inference API provider implementation.
    """

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(
            provider_name="HuggingFace",
            model_name=config.model_name
        )
        self.config = config
        self._client: Any = None

    # ========================================================
    # CLIENT INITIALIZATION
    # ========================================================

    def _initialize_client(self) -> None:
        """Lazily initialize the Hugging Face client."""
        if self._client is not None:
            return

        try:
            from huggingface_hub import InferenceClient
        except ImportError as exc:
            raise ImportError(
                "Install huggingface_hub: pip install huggingface_hub"
            ) from exc

        self._client = InferenceClient(api_key=self.config.api_key)

    def client(self) -> Any:
        self._initialize_client()
        return self._client

    # ========================================================
    # EXECUTION API
    # ========================================================

    def generate(self, prompt: str, **kwargs: Any) -> ProviderResult:
        """Generate text."""
        start = time.perf_counter()
        try:
            response = self.client().text_generation(
                prompt=prompt,
                model=self.model_name,
                max_new_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
            )
            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=True,
                content=response,
                finish_reason="stop",
                latency=time.perf_counter() - start
            )
        except Exception as exc:
            return ProviderResult(
                success=False,
                content=str(exc),
                finish_reason="error",
                latency=time.perf_counter() - start
            )

    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> ProviderResult:
        """Execute chat by formatting as prompt."""
        prompt = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages])
        return self.generate(prompt, **kwargs)

    def embed(self, text: str, **kwargs: Any) -> ProviderResult:
        """Generate embeddings using feature extraction."""
        try:
            embedding = self.client().feature_extraction(
                text, 
                model=kwargs.get("embedding_model", self.model_name)
            )
            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=True,
                metadata={"embedding": embedding}
            )
        except Exception as exc:
            return ProviderResult(success=False, content=str(exc))

    # ========================================================
    # HEALTH & UTILITIES
    # ========================================================

    def health_check(self) -> bool:
        try:
            self.client()
            return True
        except Exception:
            return False

    def supports_embeddings(self) -> bool: return True
    def supports_streaming(self) -> bool: return True

    def reset(self) -> None:
        self._client = None
        self.metadata.clear()

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "config": self.config.to_dict(),
            "client_initialized": self._client is not None,
        })
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)