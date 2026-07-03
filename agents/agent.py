"""
Distributed Agentic Reasoning Framework (DARF)

Agent Interface

Purpose
-------
Defines the canonical interface implemented by every
agent in DARF.
"""

from __future__ import annotations

import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Framework Components
from agents.agent_capability import AgentCapability
from agents.agent_context import AgentContext
from agents.agent_policy import AgentPolicy
from agents.agent_result import AgentResult
from execution.execution_context import ExecutionContext

__all__ = ["Agent"]

# ============================================================
# AGENT
# ============================================================

@dataclass(slots=True)
class Agent(ABC):
    """
    Canonical DARF agent (Abstract Base Class).
    
    All concrete agents must implement `agent_id` and `run`.
    """

    # --- Identity ---
    _agent_id: str = field(
        default_factory=lambda: f"AGENT-{uuid.uuid4().hex.upper()}"
    )

    name: str = "agent"
    description: str = ""
    version: str = "1.0"

    # --- Infrastructure ---
    capabilities: List[AgentCapability] = field(default_factory=list)
    context: AgentContext = field(default_factory=AgentContext)
    policy: AgentPolicy = field(default_factory=AgentPolicy)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate agent initialization."""
        if not self.name.strip():
            raise ValueError("Agent name cannot be empty.")

    # ============================================================
    # ABSTRACT INTERFACE
    # ============================================================

    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Unique agent identifier."""
        return self._agent_id

    @abstractmethod
    def run(self, context: ExecutionContext, **kwargs: Any) -> Any:
        """Execute the agent logic."""
        pass

    # ============================================================
    # CAPABILITIES
    # ============================================================

    def add_capability(self, capability: AgentCapability) -> None:
        self.capabilities.append(capability)

    def has_capability(self, name: str) -> bool:
        return any(capability.matches(name) for capability in self.capabilities)

    def capability_count(self) -> int:
        return len(self.capabilities)

    # ============================================================
    # SERIALIZATION
    # ============================================================

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": [c.to_dict() for c in self.capabilities],
            "context": self.context.to_dict(),
            "policy": self.policy.to_dict(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ============================================================
    # REPRESENTATION
    # ============================================================

    def __str__(self) -> str:
        return f"Agent({self.name})"

    def __repr__(self) -> str:
        return f"<Agent name='{self.name}' capabilities={self.capability_count()}>"