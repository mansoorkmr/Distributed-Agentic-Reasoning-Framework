"""
Institutional-Grade Task Delegator
==================================

Distributed Agentic Reasoning Framework (DARF)

Responsibilities:
- Capability-aware delegation
- Hierarchical task routing
- Distributed execution assignment
- Workload balancing
- Failure-aware orchestration
- Intelligent swarm coordination
"""

from __future__ import annotations

import asyncio
import statistics
import time
import uuid

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


# ============================================================
# DELEGATION STRATEGY
# ============================================================


class DelegationStrategy(str, Enum):
    """
    Supported delegation strategies.
    """

    ROUND_ROBIN = "round_robin"

    CAPABILITY_BASED = (
        "capability_based"
    )

    LOAD_BALANCED = (
        "load_balanced"
    )

    HIERARCHICAL = "hierarchical"

    HYBRID = "hybrid"


# ============================================================
# AGENT CAPABILITY PROFILE
# ============================================================


@dataclass(slots=True)
class AgentCapabilityProfile:
    """
    Swarm agent capability descriptor.
    """

    agent_id: str

    capabilities: List[str]

    current_workload: int = 0

    reliability_score: float = 1.0

    average_latency: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# DELEGATION TASK
# ============================================================


@dataclass(slots=True)
class DelegationTask:
    """
    Distributed execution task.
    """

    task_id: str

    objective: str

    required_capabilities: List[
        str
    ]

    priority: int = 1

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at: float = field(
        default_factory=time.time
    )


# ============================================================
# DELEGATION RESULT
# ============================================================


@dataclass(slots=True)
class DelegationResult:
    """
    Delegation assignment result.
    """

    delegation_id: str

    assigned_agent_id: str

    strategy_used: DelegationStrategy

    delegation_time: float

    confidence_score: float

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# DELEGATION STATS
# ============================================================


@dataclass(slots=True)
class DelegationStats:
    """
    Delegation engine metrics.
    """

    total_delegations: int = 0

    successful_assignments: int = 0

    failed_assignments: int = 0

    average_confidence: float = 0.0


# ============================================================
# TASK DELEGATOR
# ============================================================


class TaskDelegator:
    """
    Institutional distributed delegation runtime.

    Features:
    - capability-aware assignment
    - workload balancing
    - intelligent routing
    - distributed orchestration
    """

    def __init__(
        self,
    ) -> None:

        self._agents: Dict[
            str,
            AgentCapabilityProfile,
        ] = {}

        self._round_robin_index = 0

        self._stats = (
            DelegationStats()
        )

        self._lock = asyncio.Lock()

    # ========================================================
    # AGENT REGISTRATION
    # ========================================================

    async def register_agent(
        self,
        profile: AgentCapabilityProfile,
    ) -> None:
        """
        Register agent capability profile.
        """

        async with self._lock:

            self._agents[
                profile.agent_id
            ] = profile

    async def unregister_agent(
        self,
        agent_id: str,
    ) -> bool:
        """
        Remove capability profile.
        """

        async with self._lock:

            if (
                agent_id
                not in self._agents
            ):
                return False

            del self._agents[
                agent_id
            ]

            return True

    # ========================================================
    # TASK DELEGATION
    # ========================================================

    async def delegate_task(
        self,
        task: DelegationTask,
        strategy: DelegationStrategy = (
            DelegationStrategy.HYBRID
        ),
    ) -> DelegationResult:
        """
        Execute intelligent delegation.
        """

        started_at = time.time()

        if not self._agents:

            raise ValueError(
                "No swarm agents registered."
            )

        if (
            strategy
            == DelegationStrategy.ROUND_ROBIN
        ):

            selected = (
                await self._round_robin_selection()
            )

        elif (
            strategy
            == DelegationStrategy.CAPABILITY_BASED
        ):

            selected = (
                await self._capability_selection(
                    task
                )
            )

        elif (
            strategy
            == DelegationStrategy.LOAD_BALANCED
        ):

            selected = (
                await self._load_balanced_selection()
            )

        else:

            selected = (
                await self._hybrid_selection(
                    task
                )
            )

        confidence = (
            await self._calculate_confidence(
                selected
            )
        )

        async with self._lock:

            selected.current_workload += 1

            self._stats.total_delegations += 1

            self._stats.successful_assignments += 1

            self._update_average_confidence(
                confidence
            )

        return DelegationResult(
            delegation_id=str(uuid.uuid4()),
            assigned_agent_id=(
                selected.agent_id
            ),
            strategy_used=strategy,
            delegation_time=(
                time.time()
                - started_at
            ),
            confidence_score=confidence,
            metadata={
                "capabilities": (
                    selected.capabilities
                ),
            },
        )

    # ========================================================
    # ROUND ROBIN
    # ========================================================

    async def _round_robin_selection(
        self,
    ) -> AgentCapabilityProfile:
        """
        Round-robin routing.
        """

        agents = list(
            self._agents.values()
        )

        index = (
            self._round_robin_index
            % len(agents)
        )

        self._round_robin_index += 1

        return agents[index]

    # ========================================================
    # CAPABILITY ROUTING
    # ========================================================

    async def _capability_selection(
        self,
        task: DelegationTask,
    ) -> AgentCapabilityProfile:
        """
        Capability-aware selection.
        """

        compatible = []

        for agent in self._agents.values():

            if all(
                capability
                in agent.capabilities
                for capability
                in task.required_capabilities
            ):

                compatible.append(agent)

        if not compatible:

            raise ValueError(
                "No capable agents found."
            )

        return max(
            compatible,
            key=lambda agent: (
                agent.reliability_score
            ),
        )

    # ========================================================
    # LOAD BALANCING
    # ========================================================

    async def _load_balanced_selection(
        self,
    ) -> AgentCapabilityProfile:
        """
        Workload-balanced selection.
        """

        return min(
            self._agents.values(),
            key=lambda agent: (
                agent.current_workload
            ),
        )

    # ========================================================
    # HYBRID ROUTING
    # ========================================================

    async def _hybrid_selection(
        self,
        task: DelegationTask,
    ) -> AgentCapabilityProfile:
        """
        Institutional hybrid routing.
        """

        compatible = []

        for agent in self._agents.values():

            if all(
                capability
                in agent.capabilities
                for capability
                in task.required_capabilities
            ):

                compatible.append(agent)

        if not compatible:

            compatible = list(
                self._agents.values()
            )

        return max(
            compatible,
            key=lambda agent: (
                (
                    agent.reliability_score
                    * 0.7
                )
                - (
                    agent.current_workload
                    * 0.3
                )
            ),
        )

    # ========================================================
    # CONFIDENCE ESTIMATION
    # ========================================================

    async def _calculate_confidence(
        self,
        profile: AgentCapabilityProfile,
    ) -> float:
        """
        Estimate delegation confidence.
        """

        workload_penalty = min(
            profile.current_workload
            * 0.05,
            0.5,
        )

        confidence = (
            profile.reliability_score
            - workload_penalty
        )

        return max(
            0.0,
            min(confidence, 1.0),
        )

    # ========================================================
    # EXECUTION COMPLETION
    # ========================================================

    async def mark_task_completed(
        self,
        agent_id: str,
    ) -> None:
        """
        Release workload allocation.
        """

        async with self._lock:

            agent = self._agents.get(
                agent_id
            )

            if not agent:
                return

            agent.current_workload = max(
                0,
                agent.current_workload
                - 1,
            )

    # ========================================================
    # METRICS
    # ========================================================

    def _update_average_confidence(
        self,
        confidence: float,
    ) -> None:
        """
        Update runtime metrics.
        """

        total = (
            self._stats.total_delegations
        )

        if total <= 1:

            self._stats.average_confidence = (
                confidence
            )

            return

        current = (
            self._stats.average_confidence
        )

        self._stats.average_confidence = (
            (
                current
                * (total - 1)
            )
            + confidence
        ) / total

    # ========================================================
    # AGENT ANALYTICS
    # ========================================================

    async def get_agent_profiles(
        self,
    ) -> List[
        AgentCapabilityProfile
    ]:
        """
        Retrieve capability profiles.
        """

        async with self._lock:

            return list(
                self._agents.values()
            )

    # ========================================================
    # STATS
    # ========================================================

    def get_stats(
        self,
    ) -> DelegationStats:
        """
        Retrieve delegation metrics.
        """

        return self._stats

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    async def health_check(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime diagnostics.
        """

        workloads = [
            profile.current_workload
            for profile
            in self._agents.values()
        ]

        avg_workload = (
            statistics.mean(workloads)
            if workloads
            else 0.0
        )

        return {
            "status": "healthy",
            "registered_agents": len(
                self._agents
            ),
            "total_delegations": (
                self._stats.total_delegations
            ),
            "successful_assignments": (
                self._stats.successful_assignments
            ),
            "average_confidence": (
                self._stats.average_confidence
            ),
            "average_workload": (
                avg_workload
            ),
        }
