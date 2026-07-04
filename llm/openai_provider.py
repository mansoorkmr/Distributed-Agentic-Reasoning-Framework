"""
Distributed Agentic Reasoning Framework (DARF)

OpenAI Provider

Production implementation of the DARF LLMProvider interface 
using the official OpenAI Python SDK.
"""

from __future__ import annotations

import time
import json
from typing import Any, Dict, List, Optional

from llm.provider import LLMProvider
from llm.provider_config import ProviderConfig
from llm.provider_result import ProviderResult

__all__ = ["OpenAIProvider"]

class OpenAIProvider(LLMProvider):
    """
    Production-ready OpenAI provider implementation.
    """

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(
            provider_name="OpenAI",
            model_name=config.model_name
        )
        self.config = config
        self.client: Any = None

    # ========================================================
    # CLIENT INITIALIZATION
    # ========================================================

    def _create_client(self) -> None:
        """Lazily create the OpenAI client."""
        if self.client is not None:
            return

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "OpenAI SDK not installed. Run: pip install openai"
            ) from exc

        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            organization=self.config.organization,
        )

    # ========================================================
    # HEALTH & STATUS
    # ========================================================

    def health_check(self) -> bool:
        """Verify provider reachability."""
        try:
            self._create_client()
            self.client.models.list()
            return True
        except Exception:
            return False

    def configured(self) -> bool:
        """Check if provider configuration is valid."""
        return self.config.has_api_key() and bool(self.config.model_name)

    # ========================================================
    # EXECUTION API
    # ========================================================

    def generate(self, prompt: str, **kwargs: Any) -> ProviderResult:
        """Generate text using Chat Completions API."""
        self._create_client()
        start = time.perf_counter()

        try:
            response = self.client.chat.completions.create(
                model=kwargs.get("model", self.config.model_name),
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
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
                latency=latency,
                metadata={"response_id": response.id}
            )

        except Exception as exc:
            import traceback

            print("\n")
            print("=" * 80)
            print("OPENAI ERROR")
            traceback.print_exc()
            print("=" * 80)

            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=False,
                content=str(exc),
                finish_reason="error",
                latency=time.perf_counter() - start,
            )

    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> ProviderResult:
        """Execute a chat completion."""
        self._create_client()
        start = time.perf_counter()
        
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get("model", self.config.model_name),
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
        self._create_client()
        start = time.perf_counter()
        
        try:
            response = self.client.embeddings.create(
                input=text, 
                model=kwargs.get("model", "text-embedding-3-small")
            )
            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=True,
                latency=time.perf_counter() - start,
                metadata={"embedding": response.data[0].embedding}
            )
        except Exception as exc:
            return ProviderResult(success=False, content=str(exc))

    # ========================================================
    # SERIALIZATION & REPRESENTATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "configured": self.configured(),
            "config": self.config.to_dict(),
            "client_initialized": self.client is not None,
        })
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)