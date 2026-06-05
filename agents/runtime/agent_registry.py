"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Agent Registry

Author:
    DARF Runtime Systems Division

Purpose:
    Enterprise-grade agent discovery, registration,
    validation, lifecycle coordination, and
    runtime integration.

Responsibilities:
    - agent registration
    - agent discovery
    - agent lookup
    - contract validation
    - lifecycle integration
    - runtime synchronization
    - distributed-safe access
    - registry observability

Design Patterns:
    - Registry Pattern
    - Repository Pattern
    - Dependency Inversion Pattern
    - Contract Validation Pattern

Complexity:
    register_agent()      O(1)
    unregister_agent()    O(1)
    get_agent()           O(1)
    exists()              O(1)
    list_agents()         O(n)
"""

from __future__ import annotations

import asyncio

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from typing import Dict
from typing import List
from typing import Optional
from typing import Any

from agents.base_agent import BaseAgent

from agents.runtime.lifecycle_manager import (
    AgentLifecycleManager,
    AgentLifecycleState,
)

from agents.runtime.exceptions import (
    AgentAlreadyRegisteredError,
    AgentNotFoundError,
    AgentRegistrationError,
    RuntimeValidationError,
)


# ============================================================
# REGISTRY RECORD
# ============================================================


@dataclass(slots=True)
class AgentRegistryRecord:
    """
    Immutable registry record.

    Complexity:
        O(1)
    """

    agent_id: str

    agent_name: str

    registered_at: str = field(
        default_factory=lambda:
        datetime.utcnow().isoformat()
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# AGENT REGISTRY
# ============================================================


class AgentRegistry:
    """
    Institutional-grade registry.

    Guarantees:
        - unique registration
        - lifecycle synchronization
        - thread-safe access
        - runtime-safe lookup
        - strong typing
    """

    def __init__(
        self,
        lifecycle_manager:
        Optional[
            AgentLifecycleManager
        ] = None,
    ) -> None:

        self._agents: Dict[
            str,
            BaseAgent
        ] = {}

        self._records: Dict[
            str,
            AgentRegistryRecord
        ] = {}

        self._lifecycle = (
            lifecycle_manager
            or AgentLifecycleManager()
        )

        self._lock = asyncio.Lock()

    # ========================================================
    # VALIDATION
    # ========================================================

    def _validate_agent_id(
        self,
        agent_id: str,
    ) -> None:

        if not isinstance(
            agent_id,
            str,
        ):

            raise RuntimeValidationError(
                "agent_id must be string"
            )

        if not agent_id.strip():

            raise RuntimeValidationError(
                "agent_id cannot be empty"
            )

    def _validate_agent(
        self,
        agent: BaseAgent,
    ) -> None:

        if not isinstance(
            agent,
            BaseAgent,
        ):

            raise AgentRegistrationError(
                "Agent must inherit "
                "BaseAgent"
            )

    # ========================================================
    # REGISTRATION
    # ========================================================

    async def register_agent(
        self,
        agent_id: str,
        agent: BaseAgent,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        self._validate_agent_id(
            agent_id
        )

        self._validate_agent(
            agent
        )

        async with self._lock:

            if (
                agent_id
                in self._agents
            ):

                raise (
                    AgentAlreadyRegisteredError(
                        f"Agent already "
                        f"registered: "
                        f"{agent_id}"
                    )
                )

            self._agents[
                agent_id
            ] = agent

            self._records[
                agent_id
            ] = AgentRegistryRecord(
                agent_id=agent_id,
                agent_name=agent.name,
                metadata=metadata
                or {},
            )

            await self._lifecycle.register_agent(
                agent_id
            )

            await self._lifecycle.transition(
                agent_id,
                AgentLifecycleState.INITIALIZING,
                reason="registered",
            )

            await self._lifecycle.transition(
                agent_id,
                AgentLifecycleState.IDLE,
                reason="ready",
            )

    # ========================================================
    # REMOVAL
    # ========================================================

    async def unregister_agent(
        self,
        agent_id: str,
    ) -> None:

        self._validate_agent_id(
            agent_id
        )

        async with self._lock:

            if (
                agent_id
                not in self._agents
            ):

                raise (
                    AgentNotFoundError(
                        f"Unknown agent: "
                        f"{agent_id}"
                    )
                )

            record = (
                await self._lifecycle
                .get_record(
                    agent_id
                )
            )

            if (
                record
                and
                record.state
                != AgentLifecycleState.SHUTDOWN
            ):

                try:

                    await self._lifecycle.transition(
                        agent_id,
                        AgentLifecycleState.SHUTDOWN,
                        reason="unregistered",
                    )

                except Exception as exc:

                    raise AgentRegistrationError(
                        f"Failed lifecycle shutdown "
                        f"for agent '{agent_id}': "
                        f"{exc}"
                    ) from exc

            self._agents.pop(
                agent_id,
                None,
            )

            self._records.pop(
                agent_id,
                None,
            )

            await self._lifecycle.unregister_agent(
                agent_id
            )
    # ========================================================
    # LOOKUP
    # ========================================================

    def get_agent(
        self,
        agent_id: str,
    ) -> BaseAgent:

        agent = self._agents.get(
            agent_id
        )

        if agent is None:

            raise (
                AgentNotFoundError(
                    f"Agent not found: "
                    f"{agent_id}"
                )
            )

        return agent

    def get_record(
        self,
        agent_id: str,
    ) -> AgentRegistryRecord:

        record = self._records.get(
            agent_id
        )

        if record is None:

            raise (
                AgentNotFoundError(
                    f"Registry record "
                    f"not found: "
                    f"{agent_id}"
                )
            )

        return record

    # ========================================================
    # EXISTENCE
    # ========================================================

    def exists(
        self,
        agent_id: str,
    ) -> bool:

        return (
            agent_id
            in self._agents
        )

    # ========================================================
    # LISTING
    # ========================================================

    def list_agents(
        self,
    ) -> List[str]:

        return sorted(
            self._agents.keys()
        )

    def list_records(
        self,
    ) -> List[
        AgentRegistryRecord
    ]:

        return sorted(
            self._records.values(),
            key=lambda r: (
                r.agent_id
            ),
        )

    # ========================================================
    # COUNTS
    # ========================================================

    def count(
        self,
    ) -> int:

        return len(
            self._agents
        )

    # ========================================================
    # SNAPSHOT
    # ========================================================

    async def snapshot(
        self,
    ) -> Dict[str, Any]:

        lifecycle = (
            await self._lifecycle.metrics()
        )

        return {

            "registered_agents":
                self.count(),

            "agent_ids":
                self.list_agents(),

            "lifecycle":
                lifecycle,
        }

    # ========================================================
    # HEALTH
    # ========================================================

    async def health_check(
        self,
    ) -> Dict[str, Any]:

        lifecycle = (
            await self._lifecycle.health_check()
        )

        return {

            "status":
                "healthy",

            "registered_agents":
                self.count(),

            "lifecycle":
                lifecycle,
        }

    # ========================================================
    # STRING
    # ========================================================

    def __len__(
        self,
    ) -> int:

        return self.count()

    def __contains__(
        self,
        agent_id: str,
    ) -> bool:

        return self.exists(
            agent_id
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"AgentRegistry("
            f"agents="
            f"{self.count()}"
            f")"
        )
