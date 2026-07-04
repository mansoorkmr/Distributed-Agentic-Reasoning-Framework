"""
Distributed Agentic Reasoning Framework (DARF)

Ollama Provider
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List

import requests

from config import settings
from llm.provider import LLMProvider
from llm.provider_config import ProviderConfig
from llm.provider_result import ProviderResult


class OllamaProvider(LLMProvider):

    def __init__(self, config: ProviderConfig):

        super().__init__(
            provider_name="Ollama",
            model_name=config.model_name,
        )

        self.config = config

    def configured(self) -> bool:
        return True

    def health_check(self) -> bool:
        try:
            r = requests.get(
                f"{self.config.base_url}/api/tags",
                timeout=5,
            )
            return r.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, **kwargs: Any) -> ProviderResult:

        start = time.perf_counter()

        payload = {
            "model": kwargs.get(
                "model",
                self.config.model_name,
            ),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get(
                    "temperature",
                    self.config.temperature,
                )
            },
        }

        try:

            r = requests.post(
                f"{self.config.base_url}/api/generate",
                json=payload,
                timeout=300,
            )

            r.raise_for_status()

            data = r.json()

            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=True,
                content=data["response"],
                finish_reason="stop",
                latency=time.perf_counter() - start,
            )

        except Exception as exc:

            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=False,
                content=str(exc),
                finish_reason="error",
                latency=time.perf_counter() - start,
            )

    def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> ProviderResult:
        """
        Execute a chat conversation using Ollama.
        """

        start = time.perf_counter()

        payload = {
            "model": kwargs.get(
                "model",
                self.config.model_name,
            ),
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get(
                    "temperature",
                    self.config.temperature,
                )
            },
        }

        try:

            r = requests.post(
                f"{self.config.base_url}/api/chat",
                json=payload,
                timeout=300,
            )

            r.raise_for_status()

            data = r.json()

            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=True,
                content=data["message"]["content"],
                finish_reason="stop",
                latency=time.perf_counter() - start,
            )

        except Exception as exc:

            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=False,
                content=str(exc),
                finish_reason="error",
                latency=time.perf_counter() - start,
            )

    def embed(
        self,
        text: str,
        **kwargs: Any,
    ) -> ProviderResult:
        """
        Ollama embedding API.
        """

        start = time.perf_counter()

        payload = {
            "model": kwargs.get(
                "model",
                self.config.model_name,
            ),
            "input": text,
        }

        try:

            r = requests.post(
                f"{self.config.base_url}/api/embed",
                json=payload,
                timeout=300,
            )

            r.raise_for_status()

            data = r.json()

            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=True,
                latency=time.perf_counter() - start,
                metadata={
                    "embedding": data.get("embeddings"),
                },
            )

        except Exception as exc:

            return ProviderResult(
                provider_name=self.provider_name,
                model_name=self.model_name,
                success=False,
                content=str(exc),
                finish_reason="error",
                latency=time.perf_counter() - start,
            )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "provider": self.provider_name,
            "model": self.model_name,
            "configured": self.configured(),
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            indent=4,
        )