"""
Distributed Agentic Reasoning Framework (DARF)

LLM Agent

Purpose
-------
Provides the canonical Large Language Model interface for DARF.

Responsibilities
----------------
- Execute prompts
- Invoke configured LLM backend dynamically
- Return text responses and reasoning
- Support multiple providers (OpenAI, Ollama, HuggingFace, etc.)

Design Principles
-----------------
- Provider-independent abstraction
- Stateless execution
- Production-ready observability

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
from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent
from agents.agent_context import AgentContext

__all__ = ["LLMAgent"]

# ============================================================
# LLM AGENT
# ============================================================

@dataclass(slots=True)
class LLMAgent(BaseAgent):
    """
    Canonical DARF LLM Agent.
    Abstracts LLM inference to allow seamless swapping of providers.
    """

    # Override BaseAgent defaults natively to maintain perfect dataclass inheritance
    id: str = "llm"
    name: str = "LLM Agent"
    description: str = "Executes prompts using configured LLM providers."
    version: str = "1.0"

    provider: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ========================================================
    # EXECUTION
    # ========================================================

    def generate(self, prompt: str, **kwargs: Any) -> Any:
        """
        Generate a response using the configured provider.
        """
        if self.provider is None:
            raise RuntimeError("No LLM provider configured.")

        if not hasattr(self.provider, "generate"):
            raise AttributeError("Provider must implement a 'generate()' method.")

        return self.provider.generate(prompt, **kwargs)

    def run(self, context: AgentContext, **kwargs: Any) -> Any:
        """
        Execute an LLM prompt within the DARF execution flow.
        """
        # Safely pop 'prompt' to prevent duplicate kwargs collisions
        prompt = kwargs.pop("prompt", None)

        if prompt is None:
            prompt = context.get("prompt")

        if prompt is None:
            raise ValueError("No prompt supplied to the LLMAgent.")

        # Store the active prompt in the context for logging/debugging
        context.set("prompt", prompt)

        response = self.generate(prompt, **kwargs)

        # Store the result in the shared context
        context.set_output(self.agent_id, response)

        return response

    # ========================================================
    # PROVIDER UTILITIES
    # ========================================================

    def provider_ready(self) -> bool:
        """Determine whether an LLM provider is configured."""
        return self.provider is not None

    def set_provider(self, provider: Any) -> None:
        """Configure the active LLM provider."""
        if provider is None:
            raise ValueError("provider cannot be None.")
        self.provider = provider

    def clear_provider(self) -> None:
        """Remove the configured provider."""
        self.provider = None

    def reset(self) -> None:
        """Reset the LLM agent state."""
        self.clear_provider()
        self.metadata.clear()

    def get_capabilities(self) -> List[str]:
        """Return supported capabilities."""
        return [
            "text_generation",
            "chat_completion",
            "reasoning",
            "prompt_execution",
            "provider_management",
        ]

    def supports(self, capability: str) -> bool:
        """Determine whether a capability is supported."""
        return capability in self.get_capabilities()

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the LLM agent."""
        provider_name = None
        if self.provider is not None:
            provider_name = self.provider.__class__.__name__

        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "provider_ready": self.provider_ready(),
            "provider": provider_name,
            "supported_capabilities": self.get_capabilities(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        """Serialize the LLM agent to JSON."""
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"LLMAgent(ready={self.provider_ready()})"

    def __repr__(self) -> str:
        """Developer representation."""
        provider_name = None
        if self.provider is not None:
            provider_name = self.provider.__class__.__name__

        return f"<LLMAgent id='{self.agent_id}' provider={provider_name!r}>"