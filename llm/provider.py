"""
Distributed Agentic Reasoning Framework (DARF)

LLM Provider

Purpose
-------
Defines the abstract interface implemented by every
Large Language Model provider.

Supported Providers
-------------------
- OpenAI
- Azure OpenAI
- Ollama
- HuggingFace
- Llama.cpp
- Gemini
- Custom Providers

Design Principles
-----------------
- Provider independent
- Stateless interface
- Production-ready
- Easily extensible

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

__all__ = ["LLMProvider"]

# ============================================================
# ABSTRACT PROVIDER
# ============================================================

@dataclass(slots=True)
class LLMProvider(ABC):
    """
    Abstract base class for every DARF LLM provider.
    """

    provider_name: str = "Unknown"
    model_name: str = "Unknown"
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    # ========================================================
    # ABSTRACT API
    # ========================================================

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> Any:
        """
        Generate a response for a prompt.
        Must be implemented by every provider.
        """
        raise NotImplementedError

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Any:
        """
        Execute a chat completion.
        Messages follow the standard role-based format:
        [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."}
        ]
        """
        raise NotImplementedError

    @abstractmethod
    def embed(self, text: str, **kwargs: Any) -> Any:
        """
        Generate embeddings.
        Optional for providers that support embeddings.
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """
        Verify the provider is available and reachable.
        """
        raise NotImplementedError

    # ========================================================
    # PROVIDER UTILITIES
    # ========================================================

    def provider_ready(self) -> bool:
        """Determine whether the provider is operational."""
        try:
            return bool(self.health_check())
        except Exception:
            return False

    def supports_chat(self) -> bool:
        """Whether the provider supports chat completion."""
        return True

    def supports_embeddings(self) -> bool:
        """Whether the provider supports embeddings. Override if needed."""
        return False

    def supports_streaming(self) -> bool:
        """Whether the provider supports streaming responses. Override if needed."""
        return False

    def supports_multimodal(self) -> bool:
        """Whether the provider supports multimodal inputs. Override if needed."""
        return False

    def reset(self) -> None:
        """Reset provider state."""
        self.metadata.clear()

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the provider state."""
        return {
            "provider_name": self.provider_name,
            "model_name": self.model_name,
            "provider_ready": self.provider_ready(),
            "supports_chat": self.supports_chat(),
            "supports_embeddings": self.supports_embeddings(),
            "supports_streaming": self.supports_streaming(),
            "supports_multimodal": self.supports_multimodal(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        """Serialize the provider to JSON."""
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.provider_name}({self.model_name})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"<LLMProvider name='{self.provider_name}' model='{self.model_name}'>"