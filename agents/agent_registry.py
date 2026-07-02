"""
Distributed Agentic Reasoning Framework (DARF)
Agent Runtime

Agent Registry

Purpose
-------
Defines the canonical registry used to manage DARF
agents.

Responsibilities
----------------
- Agent registration
- Agent lookup
- Capability search
- Registry management

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from agents.agent import Agent

__all__ = [
    "AgentRegistry",
]
# ============================================================
# AGENT REGISTRY
# ============================================================


@dataclass(slots=True)
class AgentRegistry:
    """
    Canonical agent registry.
    """

    agents: Dict[
        str,
        Agent,
    ] = field(
        default_factory=dict
    )

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
        # ========================================================
    # REGISTRATION
    # ========================================================

    def register(
        self,
        agent: Agent,
    ) -> None:

        self.agents[
            agent.agent_id
        ] = agent

    def unregister(
        self,
        agent_id: str,
    ) -> None:

        self.agents.pop(
            agent_id,
            None,
        )
          # ========================================================
    # LOOKUP
    # ========================================================

    def get(
        self,
        agent_id: str,
    ) -> Optional[
        Agent
    ]:

        return self.agents.get(
            agent_id
        )

    def find_by_name(
        self,
        name: str,
    ) -> Optional[
        Agent
    ]:

        for agent in self.agents.values():

            if (
                agent.name.lower()
                == name.lower()
            ):

                return agent

        return None

    def find_by_capability(
        self,
        capability: str,
    ) -> List[
        Agent
    ]:

        return [

            agent

            for agent

            in self.agents.values()

            if agent.has_capability(
                capability
            )

        ]
          # ========================================================
    # HELPERS
    # ========================================================

    def count(
        self,
    ) -> int:

        return len(
            self.agents
        )

    def is_empty(
        self,
    ) -> bool:

        return (
            self.count()
            == 0
        )

    def clear(
        self,
    ) -> None:

        self.agents.clear()
            # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[
        str,
        Any,
    ]:

        return {

            "agents": [

                agent.to_dict()

                for agent

                in self.agents.values()

            ],

            "count": self.count(),

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
            f"AgentRegistry("
            f"{self.count()} agents)"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<AgentRegistry "
            f"count={self.count()}>"
        )