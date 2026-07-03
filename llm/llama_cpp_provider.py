"""
Distributed Agentic Reasoning Framework (DARF)

Llama.cpp Provider

Purpose
-------
Production implementation of the DARF LLMProvider interface
using the llama-cpp-python library for local GGUF model execution.

Responsibilities
----------------
- Load GGUF models directly into memory
- Generate text, chat, and embeddings locally
- Manage local compute resources (n_ctx)

Design Principles
-----------------
- Zero network latency
- Privacy-first (100% local)
- Standardized DARF interface
- Production-ready resource management

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import time
import json
from typing import Any, Dict, List, Optional

from llm.provider import LLMProvider
from llm.provider_config import ProviderConfig
from llm.provider_result import ProviderResult

__all__ = ["LlamaCppProvider"]

class LlamaCppProvider(LLMProvider):
    """
    Production-ready local GGUF provider implementation.
    """

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(
            provider_name="LlamaCpp",
            model_name=config.model_name
        )
        self.config = config
        self._client: Any = None

    # ========================================================
    # CLIENT INITIALIZATION
    # ========================================================

    def initialize(self) -> None:
        """Lazily initialize the Llama.cpp client."""
        if self._client is not None:
            return

        if not self.config.base_url:
            raise ValueError("ProviderConfig.base_url must point to a GGUF model file.")

        try:
            from llama_cpp import Llama
        except ImportError as exc:
            raise ImportError(
                "Install llama-cpp-python: pip install llama-cpp-python"
            ) from exc

        self._client = Llama(
            model_path=self.config.base_url,
            n_ctx=self.config.max_tokens,
            verbose=False,
        )

    def client(self) -> Any:
        self.initialize()
        return self._client

    # ========================================================
    # EXECUTION API
    # ========================================================

    def generate(self, prompt: str, **kwargs: Any) -> ProviderResult:
        """Generate text using local model."""
        start = time.perf_counter()
        try:
            response = self.client()(
                prompt,
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
            )
            
            latency = time.perf_counter() - start
            usage = response.get("usage", {})
            
            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=True,
                content=response["choices"][0]["text"],
                finish_reason="stop",
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
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
        """Execute chat by flattening messages to prompt."""
        prompt = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages])
        return self.generate(prompt, **kwargs)

    def embed(self, text: str, **kwargs: Any) -> ProviderResult:
        """Generate local embeddings."""
        try:
            embedding = self.client().embed(text)
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