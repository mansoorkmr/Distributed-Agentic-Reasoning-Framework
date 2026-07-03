"""
Distributed Agentic Reasoning Framework (DARF)

Provider Result

Purpose
-------
Standardizes the output from all LLM providers (OpenAI, Ollama, HuggingFace, etc.)
into a single, predictable result object.

Responsibilities
----------------
- Capture generated text and structured reasoning
- Store usage metrics (tokens, latency, cost)
- Handle provider-specific metadata
- Track finish reasons

Design Principles
-----------------
- Provider-agnostic interface
- Serializable
- High-precision telemetry
- Production-ready

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

__all__ = ["ProviderResult"]

# ============================================================
# PROVIDER RESULT
# ============================================================

@dataclass(slots=True)
class ProviderResult:
    """
    Standardized response object for all DARF LLM providers.
    """

    result_id: str = field(
        default_factory=lambda: f"PROVIDERRESULT-{uuid.uuid4().hex.upper()}"
    )
    provider_name: str = ""
    model_name: str = ""
    success: bool = True
    content: Optional[str] = None
    finish_reason: Optional[str] = None
    
    # Telemetry
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency: float = 0.0
    estimated_cost: float = 0.0
    
    # Context & Debugging
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    # ========================================================
    # VALIDATION
    # ========================================================

    def __post_init__(self) -> None:
        """Validate result metrics post-initialization."""
        if self.prompt_tokens < 0:
            raise ValueError("prompt_tokens cannot be negative.")
        if self.completion_tokens < 0:
            raise ValueError("completion_tokens cannot be negative.")
        if self.total_tokens < 0:
            raise ValueError("total_tokens cannot be negative.")
        if self.latency < 0:
            raise ValueError("latency cannot be negative.")
        if self.estimated_cost < 0:
            raise ValueError("estimated_cost cannot be negative.")

        # Auto-calculate total if not provided
        if self.total_tokens == 0:
            self.total_tokens = self.prompt_tokens + self.completion_tokens

    # ========================================================
    # HELPERS
    # ========================================================

    def succeeded(self) -> bool:
        """Return whether generation succeeded."""
        return self.success

    def failed(self) -> bool:
        """Return whether generation failed."""
        return not self.success

    def has_content(self) -> bool:
        """Determine whether content exists."""
        return bool(self.content)

    def token_usage(self) -> Dict[str, int]:
        """Return token statistics."""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }

    def cost(self) -> float:
        """Return estimated execution cost."""
        return self.estimated_cost

    def reset_metadata(self) -> None:
        """Remove all metadata."""
        self.metadata.clear()

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialize result to dictionary."""
        return {
            "result_id": self.result_id,
            "provider_name": self.provider_name,
            "model_name": self.model_name,
            "success": self.success,
            "content": self.content,
            "finish_reason": self.finish_reason,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "latency": round(self.latency, 4),
            "estimated_cost": self.estimated_cost,
            "metadata": dict(self.metadata),
            "version": self.version,
        }

    def to_json(self) -> str:
        """Serialize result to JSON."""
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(self) -> str:
        state = "SUCCESS" if self.success else "FAILED"
        return f"ProviderResult({state}, {self.total_tokens} tokens)"

    def __repr__(self) -> str:
        return (
            f"<ProviderResult id='{self.result_id}' "
            f"provider='{self.provider_name}' "
            f"model='{self.model_name}' "
            f"success={self.success}>"
        )