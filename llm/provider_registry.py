"""
Distributed Agentic Reasoning Framework (DARF)

Provider Registry

Purpose
-------
Maintains the registry of all available LLM providers,
enabling dynamic lookup and runtime switching.

Responsibilities
----------------
- Register and remove LLM providers
- Lookup providers by name
- Manage default provider configuration
- Provide unified enumeration
- Serialize registry state

Design Principles
-----------------
- Provider independent
- Thread-safe (via encapsulated dict)
- Serializable
- Production-ready

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from llm.provider import LLMProvider

__all__ = ["ProviderRegistry"]


# ============================================================
# PROVIDER REGISTRY
# ============================================================

@dataclass(slots=True)
class ProviderRegistry:
    """
    Registry of available LLM providers.
    """

    providers: Dict[str, LLMProvider] = field(default_factory=dict)
    default_provider: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    # ========================================================
    # REGISTRY OPERATIONS
    # ========================================================

    def register(self, provider: LLMProvider) -> None:
        """Register an LLM provider."""
        self.providers[provider.provider_name] = provider

    def unregister(self, provider_name: str) -> bool:
        """Remove a provider. Returns True if successfully removed."""
        return self.providers.pop(provider_name, None) is not None

    def get(self, provider_name: str) -> Optional[LLMProvider]:
        """Retrieve a provider by name."""
        return self.providers.get(provider_name)

    def contains(self, provider_name: str) -> bool:
        """Determine whether a provider exists."""
        return provider_name in self.providers

    # ========================================================
    # ENUMERATION
    # ========================================================

    def names(self) -> List[str]:
        """Return a sorted list of registered provider names."""
        return sorted(self.providers.keys())

    def count(self) -> int:
        """Return the number of registered providers."""
        return len(self.providers)

    def is_empty(self) -> bool:
        """Determine whether the registry is empty."""
        return self.count() == 0

    # ========================================================
    # DEFAULT PROVIDER
    # ========================================================

    def set_default(self, provider_name: str) -> None:
        """Configure the default provider."""
        if not self.contains(provider_name):
            raise ValueError(f"Unknown provider '{provider_name}'.")
        self.default_provider = provider_name

    def get_default(self) -> Optional[LLMProvider]:
        """Return the default provider instance."""
        if self.default_provider is None:
            return None
        return self.get(self.default_provider)

    def has_default(self) -> bool:
        """Determine whether a default provider is configured."""
        return self.default_provider is not None

    def clear_default(self) -> None:
        """Remove the default provider."""
        self.default_provider = None

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the provider registry."""
        return {
            "provider_count": self.count(),
            "providers": self.names(),
            "default_provider": self.default_provider,
            "has_default": self.has_default(),
            "metadata": dict(self.metadata),
            "version": self.version,
        }

    def to_json(self) -> str:
        """Serialize the registry to JSON."""
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ========================================================
    # REPRESENTATION & PROTOCOLS
    # ========================================================

    def __len__(self) -> int:
        return self.count()

    def __contains__(self, provider_name: str) -> bool:
        return self.contains(provider_name)

    def __str__(self) -> str:
        return f"ProviderRegistry({self.count()} providers)"

    def __repr__(self) -> str:
        return (
            f"<ProviderRegistry "
            f"providers={self.count()} "
            f"default={self.default_provider!r}>"
        )