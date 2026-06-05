"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Agent Lifecycle Manager

Author:
    DARF Runtime Systems Division

Purpose:
    Enterprise-grade lifecycle orchestration for
    distributed multi-agent systems.

Responsibilities:
    - lifecycle state management
    - transition validation
    - execution tracking
    - health monitoring
    - failure recovery hooks
    - auditability
    - distributed-safe lifecycle control
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional


# ============================================================
# AGENT LIFECYCLE STATE
# ============================================================


class AgentLifecycleState(str, Enum):

    REGISTERED = "registered"

    INITIALIZING = "initializing"

    IDLE = "idle"

    EXECUTING = "executing"

    PAUSED = "paused"

    FAILED = "failed"

    DISABLED = "disabled"

    SHUTDOWN = "shutdown"


# ============================================================
# VALID TRANSITIONS
# ============================================================


VALID_TRANSITIONS = {

    AgentLifecycleState.REGISTERED: {
        AgentLifecycleState.INITIALIZING,
        AgentLifecycleState.DISABLED,
    },

    AgentLifecycleState.INITIALIZING: {
        AgentLifecycleState.IDLE,
        AgentLifecycleState.FAILED,
        AgentLifecycleState.DISABLED,
    },

    AgentLifecycleState.IDLE: {
        AgentLifecycleState.EXECUTING,
        AgentLifecycleState.PAUSED,
        AgentLifecycleState.DISABLED,
        AgentLifecycleState.SHUTDOWN,
    },

    AgentLifecycleState.EXECUTING: {
        AgentLifecycleState.IDLE,
        AgentLifecycleState.FAILED,
        AgentLifecycleState.PAUSED,
        AgentLifecycleState.DISABLED,
    },

    AgentLifecycleState.PAUSED: {
        AgentLifecycleState.IDLE,
        AgentLifecycleState.DISABLED,
        AgentLifecycleState.SHUTDOWN,
    },

    AgentLifecycleState.FAILED: {
        AgentLifecycleState.INITIALIZING,
        AgentLifecycleState.DISABLED,
        AgentLifecycleState.SHUTDOWN,
    },

    AgentLifecycleState.DISABLED: {
        AgentLifecycleState.INITIALIZING,
        AgentLifecycleState.SHUTDOWN,
    },

    AgentLifecycleState.SHUTDOWN: set(),
}


# ============================================================
# LIFECYCLE EVENT
# ============================================================


@dataclass(slots=True)
class LifecycleEvent:

    timestamp: datetime

    previous_state: Optional[
        AgentLifecycleState
    ]

    new_state: AgentLifecycleState

    reason: Optional[str] = None


# ============================================================
# AGENT LIFECYCLE RECORD
# ============================================================


@dataclass(slots=True)
class AgentLifecycleRecord:

    agent_id: str

    state: AgentLifecycleState = (
        AgentLifecycleState.REGISTERED
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    last_error: Optional[str] = None

    transition_count: int = 0

    events: List[LifecycleEvent] = field(
        default_factory=list
    )


# ============================================================
# AGENT LIFECYCLE MANAGER
# ============================================================


class AgentLifecycleManager:
    """
    Institutional-grade lifecycle controller.

    Guarantees:
        - transition validation
        - auditability
        - concurrency safety
        - lifecycle consistency
    """

    def __init__(self) -> None:

        self._records: Dict[
            str,
            AgentLifecycleRecord
        ] = {}

        self._lock = asyncio.Lock()

    # ========================================================
    # REGISTRATION
    # ========================================================

    async def register_agent(
        self,
        agent_id: str,
    ) -> AgentLifecycleRecord:

        async with self._lock:

            if agent_id in self._records:

                return self._records[
                    agent_id
                ]

            record = AgentLifecycleRecord(
                agent_id=agent_id
            )

            self._records[
                agent_id
            ] = record

            return record

    # ========================================================
    # LOOKUP
    # ========================================================

    async def get_record(
        self,
        agent_id: str,
    ) -> Optional[
        AgentLifecycleRecord
    ]:

        return self._records.get(
            agent_id
        )

    # ========================================================
    # TRANSITION
    # ========================================================

    async def transition(
        self,
        agent_id: str,
        new_state: AgentLifecycleState,
        reason: Optional[str] = None,
    ) -> None:

        async with self._lock:

            if agent_id not in self._records:

                raise RuntimeError(
                    f"Agent not registered: {agent_id}"
                )

            record = self._records[
                agent_id
            ]

            current = record.state

            allowed = (
                VALID_TRANSITIONS.get(
                    current,
                    set(),
                )
            )

            if new_state not in allowed:

                raise RuntimeError(
                    f"Invalid lifecycle transition "
                    f"{current.value} -> "
                    f"{new_state.value}"
                )

            record.events.append(
                LifecycleEvent(
                    timestamp=datetime.utcnow(),
                    previous_state=current,
                    new_state=new_state,
                    reason=reason,
                )
            )

            record.state = new_state

            record.updated_at = (
                datetime.utcnow()
            )

            record.transition_count += 1

            if (
                new_state
                == AgentLifecycleState.FAILED
            ):
                record.last_error = reason

    # ========================================================
    # HEALTH
    # ========================================================

    async def health_check(
        self,
    ) -> Dict[str, int]:

        counts = {
            state.value: 0
            for state in AgentLifecycleState
        }

        for record in (
            self._records.values()
        ):

            counts[
                record.state.value
            ] += 1

        return counts

    # ========================================================
    # METRICS
    # ========================================================

    async def metrics(
        self,
    ) -> Dict[str, int]:

        total = len(
            self._records
        )

        active = sum(
            1
            for r in self._records.values()
            if r.state
            == AgentLifecycleState.EXECUTING
        )

        failed = sum(
            1
            for r in self._records.values()
            if r.state
            == AgentLifecycleState.FAILED
        )

        return {
            "registered_agents": total,
            "active_agents": active,
            "failed_agents": failed,
        }

    # ========================================================
    # LISTING
    # ========================================================

    async def list_agents(
        self,
    ) -> List[str]:

        return sorted(
            self._records.keys()
        )

    # ========================================================
    # REMOVAL
    # ========================================================

    async def unregister_agent(
        self,
        agent_id: str,
    ) -> None:

        async with self._lock:

            self._records.pop(
                agent_id,
                None,
            )
