"""
Distributed Agentic Reasoning Framework (DARF)
Agent Runtime

Agent

Purpose
-------
Defines the canonical DARF agent.

Responsibilities
----------------
- Agent identity
- Agent capabilities
- Runtime context
- Runtime policy
- Execution interface

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json
import uuid

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict
from typing import List

from agents.agent_capability import AgentCapability
from agents.agent_context import AgentContext
from agents.agent_policy import AgentPolicy
from agents.agent_result import AgentResult

__all__ = [
    "Agent",
]
# ============================================================
# AGENT
# ============================================================


@dataclass(slots=True)
class Agent:
    """
    Canonical DARF agent.
    """

    agent_id: str = field(
        default_factory=lambda:
            f"AGENT-{uuid.uuid4().hex.upper()}"
    )

    name: str = "agent"

    description: str = ""

    capabilities: List[
        AgentCapability
    ] = field(
        default_factory=list
    )

    context: AgentContext = field(
        default_factory=AgentContext
    )

    policy: AgentPolicy = field(
        default_factory=AgentPolicy
    )

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"

    def __post_init__(
        self,
    ) -> None:

        if not self.name.strip():

            raise ValueError(
                "Agent name cannot be empty."
            )
            # ========================================================
    # CAPABILITIES
    # ========================================================

    def add_capability(
        self,
        capability: AgentCapability,
    ) -> None:

        self.capabilities.append(
            capability
        )

    def has_capability(
        self,
        name: str,
    ) -> bool:

        return any(
            capability.matches(name)
            for capability
            in self.capabilities
        )

    def capability_count(
        self,
    ) -> int:

        return len(
            self.capabilities
        )
        # ========================================================
    # EXECUTION
    # ========================================================

    def execute(
        self,
    ) -> AgentResult:
        """
        Default execution.

        Override in subclasses.
        """

        result = AgentResult()

        result.agent_id = self.agent_id

        result.mark_success()

        return result
        # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "agent_id": self.agent_id,

            "name": self.name,

            "description": self.description,

            "capabilities": [

                capability.to_dict()

                for capability

                in self.capabilities

            ],

            "context": self.context.to_dict(),

            "policy": self.policy.to_dict(),

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(
        self,
    ) -> str:

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

        )
        # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(
        self,
    ) -> str:

        return (

            f"Agent("

            f"{self.name})"

        )

    def __repr__(
        self,
    ) -> str:

        return (

            f"<Agent "

            f"name='{self.name}' "

            f"capabilities={self.capability_count()}>"

        )