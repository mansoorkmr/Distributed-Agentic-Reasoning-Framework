"""
Institutional-Grade Swarm Runtime
=================================

Distributed Agentic Reasoning Framework (DARF)

Responsibilities:
- Distributed swarm execution
- Runtime orchestration
- Fault tolerance
- Resource coordination
- Lifecycle management
- Institutional execution control plane
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

from agents.swarm.consensus.consensus_engine import (
    AgentOpinion,
)
from agents.swarm.consensus.consensus_engine import (
    ConsensusEngine,
)
from agents.swarm.consensus.consensus_engine import (
    ConsensusResult,
)

from agents.swarm.core.swarm_manager import (
    SwarmManager,
)
from agents.swarm.core.swarm_manager import (
    SwarmResult,
)

from agents.swarm.delegation.task_delegator import (
    DelegationResult,
)
from agents.swarm.delegation.task_delegator import (
    DelegationStrategy,
)
from agents.swarm.delegation.task_delegator import (
    TaskDelegator,
)
from agents.swarm.delegation.task_delegator import (
    DelegationTask,
)


# ============================================================
# RUNTIME STATUS
# ============================================================


class RuntimeStatus(str, Enum):
    """
    Swarm runtime states.
    """

    INITIALIZING = "initializing"

    RUNNING = "running"

    DEGRADED = "degraded"

    RECOVERING = "recovering"

    STOPPED = "stopped"


# ============================================================
# SWARM NODE
# ============================================================


@dataclass(slots=True)
class SwarmNode:
    """
    Distributed swarm node.
    """

    node_id: str

    hostname: str

    active_agents: int = 0

    cpu_utilization: float = 0.0

    memory_utilization: float = 0.0

    healthy: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# RUNTIME EXECUTION
# ============================================================


@dataclass(slots=True)
class RuntimeExecution:
    """
    Distributed runtime execution.
    """

    execution_id: str

    objective: str

    started_at: float

    completed_at: Optional[
        float
    ] = None

    success: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# RUNTIME STATS
# ============================================================


@dataclass(slots=True)
class SwarmRuntimeStats:
    """
    Runtime metrics.
    """

    total_executions: int = 0

    successful_executions: int = 0

    failed_executions: int = 0

    active_nodes: int = 0

    average_execution_time: float = 0.0

    recovery_operations: int = 0


# ============================================================
# SWARM RUNTIME
# ============================================================


class SwarmRuntime:
    """
    Institutional distributed swarm runtime.

    Features:
    - distributed execution
    - consensus orchestration
    - task delegation
    - node coordination
    - fault tolerance
    """

    def __init__(
        self,
        swarm_manager: SwarmManager,
        consensus_engine: ConsensusEngine,
        task_delegator: TaskDelegator,
    ) -> None:

        self.swarm_manager = (
            swarm_manager
        )

        self.consensus_engine = (
            consensus_engine
        )

        self.task_delegator = (
            task_delegator
        )

        self._nodes: Dict[
            str,
            SwarmNode,
        ] = {}

        self._executions: Dict[
            str,
            RuntimeExecution,
        ] = {}

        self._status = (
            RuntimeStatus.INITIALIZING
        )

        self._stats = (
            SwarmRuntimeStats()
        )

        self._lock = asyncio.Lock()

    # ========================================================
    # RUNTIME STARTUP
    # ========================================================

    async def start_runtime(
        self,
    ) -> None:
        """
        Initialize distributed runtime.
        """

        async with self._lock:

            self._status = (
                RuntimeStatus.RUNNING
            )

    async def stop_runtime(
        self,
    ) -> None:
        """
        Shutdown runtime safely.
        """

        async with self._lock:

            self._status = (
                RuntimeStatus.STOPPED
            )

    # ========================================================
    # NODE MANAGEMENT
    # ========================================================

    async def register_node(
        self,
        hostname: str,
    ) -> str:
        """
        Register distributed swarm node.
        """

        node = SwarmNode(
            node_id=str(uuid.uuid4()),
            hostname=hostname,
        )

        async with self._lock:

            self._nodes[
                node.node_id
            ] = node

            self._stats.active_nodes = len(
                self._nodes
            )

        return node.node_id

    async def unregister_node(
        self,
        node_id: str,
    ) -> bool:
        """
        Remove swarm node.
        """

        async with self._lock:

            if node_id not in self._nodes:
                return False

            del self._nodes[node_id]

            self._stats.active_nodes = len(
                self._nodes
            )

            return True

    # ========================================================
    # DISTRIBUTED EXECUTION
    # ========================================================

    async def execute_objective(
        self,
        objective: str,
        query_embedding: List[float],
    ) -> ConsensusResult:
        """
        Execute institutional swarm cognition.
        """

        execution = RuntimeExecution(
            execution_id=str(uuid.uuid4()),
            objective=objective,
            started_at=time.time(),
        )

        async with self._lock:

            self._executions[
                execution.execution_id
            ] = execution

        try:

            # =================================================
            # SWARM EXECUTION
            # =================================================

            swarm_result = (
                await self.swarm_manager.execute_swarm(
                    objective=objective,
                    query_embedding=query_embedding,
                )
            )

            # =================================================
            # BUILD AGENT OPINIONS
            # =================================================

            opinions = (
                await self._build_opinions(
                    swarm_result
                )
            )

            # =================================================
            # CONSENSUS
            # =================================================

            consensus = (
                await self.consensus_engine.build_consensus(
                    opinions=opinions,
                )
            )

            execution.completed_at = (
                time.time()
            )

            execution.success = True

            async with self._lock:

                self._stats.total_executions += 1

                self._stats.successful_executions += 1

                self._update_average_execution_time(
                    execution
                )

            return consensus

        except Exception:

            execution.completed_at = (
                time.time()
            )

            execution.success = False

            async with self._lock:

                self._stats.total_executions += 1

                self._stats.failed_executions += 1

                self._status = (
                    RuntimeStatus.DEGRADED
                )

            raise

    # ========================================================
    # OPINION BUILDING
    # ========================================================

    async def _build_opinions(
        self,
        swarm_result: SwarmResult,
    ) -> List[AgentOpinion]:
        """
        Build consensus opinions.
        """

        opinions = []

        for agent_id, output in zip(
            swarm_result.participating_agents,
            swarm_result.outputs,
        ):

            opinions.append(
                AgentOpinion(
                    agent_id=agent_id,
                    response=output,
                    confidence_score=0.85,
                )
            )

        return opinions

    # ========================================================
    # FAULT RECOVERY
    # ========================================================

    async def recover_runtime(
        self,
    ) -> None:
        """
        Runtime recovery orchestration.
        """

        async with self._lock:

            self._status = (
                RuntimeStatus.RECOVERING
            )

            self._stats.recovery_operations += 1

        await asyncio.sleep(1)

        async with self._lock:

            self._status = (
                RuntimeStatus.RUNNING
            )

    # ========================================================
    # EXECUTION ANALYTICS
    # ========================================================

    async def get_executions(
        self,
    ) -> List[RuntimeExecution]:
        """
        Retrieve runtime executions.
        """

        async with self._lock:

            return list(
                self._executions.values()
            )

    async def get_nodes(
        self,
    ) -> List[SwarmNode]:
        """
        Retrieve active nodes.
        """

        async with self._lock:

            return list(
                self._nodes.values()
            )

    # ========================================================
    # METRICS
    # ========================================================

    def _update_average_execution_time(
        self,
        execution: RuntimeExecution,
    ) -> None:
        """
        Update runtime metrics.
        """

        if not execution.completed_at:
            return

        latency = (
            execution.completed_at
            - execution.started_at
        )

        total = (
            self._stats.successful_executions
        )

        if total <= 1:

            self._stats.average_execution_time = (
                latency
            )

            return

        current = (
            self._stats.average_execution_time
        )

        self._stats.average_execution_time = (
            (
                current
                * (total - 1)
            )
            + latency
        ) / total

    # ========================================================
    # RUNTIME HEALTH
    # ========================================================

    async def health_check(
        self,
    ) -> Dict[str, Any]:
        """
        Institutional diagnostics.
        """

        node_cpu = [
            node.cpu_utilization
            for node
            in self._nodes.values()
        ]

        avg_cpu = (
            statistics.mean(node_cpu)
            if node_cpu
            else 0.0
        )

        return {
            "status": self._status,
            "registered_nodes": len(
                self._nodes
            ),
            "active_executions": len(
                [
                    execution
                    for execution
                    in self._executions.values()
                    if not execution.completed_at
                ]
            ),
            "average_cpu_utilization": (
                avg_cpu
            ),
            "successful_executions": (
                self._stats.successful_executions
            ),
            "failed_executions": (
                self._stats.failed_executions
            ),
            "recovery_operations": (
                self._stats.recovery_operations
            ),
        }

    # ========================================================
    # STATS
    # ========================================================

    def get_stats(
        self,
    ) -> SwarmRuntimeStats:
        """
        Retrieve runtime metrics.
        """

        return self._stats
