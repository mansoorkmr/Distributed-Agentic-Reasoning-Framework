"""
Distributed Agentic Reasoning Framework (DARF)

Ollama Provider

Purpose
-------
Production implementation of the DARF LLMProvider interface 
for local Ollama instances.

Responsibilities
----------------
- Initialize local Ollama client
- Generate text via Ollama models
- Execute chat completions
- Generate embeddings
- Health monitoring

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

__all__ = ["OllamaProvider"]

class OllamaProvider(LLMProvider):
    """
    Production-ready Ollama provider implementation.
    """

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(
            provider_name="Ollama",
            model_name=config.model_name
        )
        self.config = config
        self._client: Any = None

    # ========================================================
    # CLIENT INITIALIZATION
    # ========================================================

    def _initialize_client(self) -> None:
        """Lazily initialize the Ollama client."""
        if self._client is not None:
            return

        try:
            import ollama
        except ImportError as exc:
            raise ImportError(
                "Ollama SDK not installed. Run: pip install ollama"
            ) from exc

        host = self.config.base_url or "http://localhost:11434"
        self._client = ollama.Client(host=host)

    @property
    def client(self) -> Any:
        self._initialize_client()
        return self._client

    # ========================================================
    # HEALTH & STATUS
    # ========================================================

    def health_check(self) -> bool:
        """Verify the local Ollama server is reachable."""
        try:
            self.client.ps()
            return True
        except Exception:
            return False

    # ========================================================
    # EXECUTION API
    # ========================================================

    def generate(self, prompt: str, **kwargs: Any) -> ProviderResult:
        """Generate text using Ollama's generate API."""
        start = time.perf_counter()
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "top_p": kwargs.get("top_p", self.config.top_p),
                }
            )
            
            latency = time.perf_counter() - start
            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=True,
                content=response.get("response", ""),
                finish_reason="stop" if response.get("done") else None,
                prompt_tokens=response.get("prompt_eval_count", 0),
                completion_tokens=response.get("eval_count", 0),
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
        """Execute a chat completion."""
        start = time.perf_counter()
        try:
            response = self.client.chat(model=self.model_name, messages=messages, **kwargs)
            message = response.get("message", {})
            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=True,
                content=message.get("content", ""),
                prompt_tokens=response.get("prompt_eval_count", 0),
                completion_tokens=response.get("eval_count", 0),
                latency=time.perf_counter() - start
            )
        except Exception as exc:
            return ProviderResult(success=False, content=str(exc))

    def embed(self, text: str, **kwargs: Any) -> ProviderResult:
        """Generate embeddings."""
        start = time.perf_counter()
        try:
            response = self.client.embed(model=self.model_name, input=text)
            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=True,
                latency=time.perf_counter() - start,
                metadata={"embedding": response.get("embeddings", [[]])[0]}
            )
        except Exception as exc:
            return ProviderResult(success=False, content=str(exc))

    # ========================================================
    # CAPABILITIES & SERIALIZATION
    # ========================================================

    def supports_embeddings(self) -> bool: return True
    def supports_streaming(self) -> bool: return True

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "config": self.config.to_dict(),
            "client_initialized": self._client is not None,
        })
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)