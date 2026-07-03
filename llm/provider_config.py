"""
Distributed Agentic Reasoning Framework (DARF)

Provider Configuration

Purpose
-------
Defines the canonical configuration shared by all
LLM providers.

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
- Immutable-style configuration
- Serializable
- Production-ready

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

__all__ = ["ProviderConfig"]

# ============================================================
# PROVIDER CONFIGURATION
# ============================================================

@dataclass(slots=True)
class ProviderConfig:
    """
    Canonical configuration for every DARF LLM provider.
    """

    provider_name: str = "generic"
    model_name: str = ""
    
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    organization: Optional[str] = None
    api_version: Optional[str] = None

    timeout: float = 60.0
    temperature: float = 0.7
    top_p: float = 1.0
    max_tokens: int = 4096
    seed: Optional[int] = None

    streaming: bool = False
    verify_ssl: bool = True
    max_retries: int = 3

    headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    version: str = "1.0"

    # ========================================================
    # VALIDATION
    # ========================================================

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than zero.")

        if not (0.0 <= self.temperature <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0.")

        if not (0.0 <= self.top_p <= 1.0):
            raise ValueError("top_p must be between 0.0 and 1.0.")

        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be greater than zero.")

        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative.")

    # ========================================================
    # HELPERS
    # ========================================================

    def requires_api_key(self) -> bool:
        """Determine whether this provider requires an API key."""
        return self.provider_name.lower() not in {
            "ollama",
            "llama_cpp",
            "llama.cpp",
            "local",
        }

    def has_api_key(self) -> bool:
        """Determine whether an API key has been configured."""
        return bool(self.api_key)

    def endpoint(self) -> Optional[str]:
        """Return the configured endpoint."""
        return self.base_url

    def is_streaming_enabled(self) -> bool:
        """Return whether streaming responses are enabled."""
        return self.streaming

    def enable_streaming(self) -> None:
        """Enable streaming."""
        self.streaming = True

    def disable_streaming(self) -> None:
        """Disable streaming."""
        self.streaming = False

    def reset_headers(self) -> None:
        """Remove all custom headers."""
        self.headers.clear()

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the provider configuration."""
        return {
            "provider_name": self.provider_name,
            "model_name": self.model_name,
            "api_key_configured": self.has_api_key(),
            "base_url": self.base_url,
            "organization": self.organization,
            "api_version": self.api_version,
            "timeout": self.timeout,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "seed": self.seed,
            "streaming": self.streaming,
            "verify_ssl": self.verify_ssl,
            "max_retries": self.max_retries,
            "headers": dict(self.headers),
            "metadata": dict(self.metadata),
            "version": self.version,
        }

    def to_json(self) -> str:
        """Serialize configuration to JSON."""
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"ProviderConfig({self.provider_name}:{self.model_name})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"<ProviderConfig provider='{self.provider_name}' model='{self.model_name}'>"