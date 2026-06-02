"""
Institutional-Grade Supervisor Agent
====================================

Distributed Agentic Reasoning Framework (DARF)

Responsibilities:
- Executive cognition
- Strategic orchestration
- Recursive planning
- Swarm governance
- Runtime supervision
- Autonomous workflow control
"""

from __future__ import annotations

import asyncio
import time
import uuid

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from agents.reasoning.decomposition_engine import (
    DecompositionEngine,
)

from agents.reasoning.reasoning_engine import (
    ReasoningEngine,
)

from agents.swarm.consensus.consensus_engine import (
    ConsensusResult,
)

from agents.swarm.runtime.swarm_runtime import (
    SwarmRuntime,
)


# ============================================================
# EXECUTION PRIORITY
# ============================================================


class ExecutionPriority(str, Enum):
    """
    Supervisor execution priority.
    """

    LOW = "low"

    NORMAL = "normal"

    HIGH = "high"

    CRITICAL = "critical"


# ============================================================
# EXECUTION STATUS
# ============================================================


class SupervisorExecutionStatus(
    str,
    Enum,
):
    """
    Supervisor execution states.
    """

    PENDING = "pending"

    DECOMPOSING = "decomposing"

    REASONING = "reasoning"

    EXECUTING = "executing"

    VALIDATING = "validating"

    COMPLETED = "completed"

    FAILED = "failed"


# ============================================================
# EXECUTION PLAN
# ============================================================


@dataclass(slots=True)
class SupervisorExecutionPlan:
    """
    Institutional execution plan.
    """

    execution_id: str

    objective: str

    subtasks: List[str]

    priority: ExecutionPriority

    created_at: float = field(
        default_factory=time.time
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# EXECUTION RESULT
# ============================================================


@dataclass(slots=True)
class SupervisorExecutionResult:
    """
    Final execution result.
    """

    execution_id: str

    success: bool

    consensus_result: Optional[
        ConsensusResult
    ]

    execution_time: float

    status: SupervisorExecutionStatus

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SUPERVISOR METRICS
# ============================================================


@dataclass(slots=True)
class SupervisorMetrics:
    """
    Runtime supervisor metrics.
    """

    total_executions: int = 0

    successful_executions: int = 0

    failed_executions: int = 0

    recursive_plans_generated: int = 0

    average_execution_time: float = 0.0


# ============================================================
# SUPERVISOR AGENT
# ============================================================


class SupervisorAgent:
    """
    Institutional executive orchestration agent.

    Features:
    - recursive planning
    - strategic orchestration
    - autonomous supervision
    - distributed cognition
    """

    def __init__(
        self,
        swarm_runtime: SwarmRuntime,
        reasoning_engine: ReasoningEngine,
        decomposition_engine: (
            DecompositionEngine
        ),
    ) -> None:

        self.swarm_runtime = (
            swarm_runtime
        )

        self.reasoning_engine = (
            reasoning_engine
        )

        self.decomposition_engine = (
            decomposition_engine
        )

        self._metrics = (
            SupervisorMetrics()
        )

        self._active_executions: Dict[
            str,
            SupervisorExecutionPlan,
        ] = {}

        self._lock = asyncio.Lock()

    # ========================================================
    # MAIN EXECUTION PIPELINE
    # ========================================================

    async def execute_objective(
        self,
        objective: str,
        query_embedding: List[float],
        priority: ExecutionPriority = (
            ExecutionPriority.NORMAL
        ),
    ) -> SupervisorExecutionResult:
        """
        Execute institutional cognition pipeline.
        """

        started_at = time.time()

        execution_id = str(
            uuid.uuid4()
        )

        try:

            # =================================================
            # OBJECTIVE DECOMPOSITION
            # =================================================

            subtasks = (
                await self._decompose_objective(
                    objective
                )
            )

            # =================================================
            # EXECUTION PLAN
            # =================================================

            plan = (
                SupervisorExecutionPlan(
                    execution_id=execution_id,
                    objective=objective,
                    subtasks=subtasks,
                    priority=priority,
                )
            )

            async with self._lock:

                self._active_executions[
                    execution_id
                ] = plan

                self._metrics.recursive_plans_generated += 1

            # =================================================
            # STRATEGIC REASONING
            # =================================================

            reasoning_result = (
                await self._perform_reasoning(
                    objective
                )
            )

            # =================================================
            # SWARM EXECUTION
            # =================================================

            consensus_result = (
                await self.swarm_runtime.execute_objective(
                    objective=(
                        reasoning_result
                    ),
                    query_embedding=(
                        query_embedding
                    ),
                )
            )

            # =================================================
            # FINAL RESULT
            # =================================================

            execution_time = (
                time.time()
                - started_at
            )

            async with self._lock:

                self._metrics.total_executions += 1

                self._metrics.successful_executions += 1

                self._update_average_execution_time(
                    execution_time
                )

                del self._active_executions[
                    execution_id
                ]

            return (
                SupervisorExecutionResult(
                    execution_id=execution_id,
                    success=True,
                    consensus_result=(
                        consensus_result
                    ),
                    execution_time=(
                        execution_time
                    ),
                    status=(
                        SupervisorExecutionStatus.COMPLETED
                    ),
                    metadata={
                        "subtask_count": len(
                            subtasks
                        ),
                    },
                )
            )

        except Exception as error:

            execution_time = (
                time.time()
                - started_at
            )

            async with self._lock:

                self._metrics.total_executions += 1

                self._metrics.failed_executions += 1

            return (
                SupervisorExecutionResult(
                    execution_id=execution_id,
                    success=False,
                    consensus_result=None,
                    execution_time=(
                        execution_time
                    ),
                    status=(
                        SupervisorExecutionStatus.FAILED
                    ),
                    metadata={
                        "error": str(
                            error
                        ),
                    },
                )
            )

    # ========================================================
    # OBJECTIVE DECOMPOSITION
    # ========================================================

    async def _decompose_objective(
        self,
        objective: str,
    ) -> List[str]:
        """
        Recursive objective decomposition.
        """

        result = (
            await self.decomposition_engine.decompose(
                objective
            )
        )

        if (
            hasattr(
                result,
                "subtasks",
            )
        ):

            return result.subtasks

        return [objective]

    # ========================================================
    # STRATEGIC REASONING
    # ========================================================

    async def _perform_reasoning(
        self,
        objective: str,
    ) -> str:
        """
        Institutional reasoning orchestration.
        """

        reasoning = (
            await self.reasoning_engine.reason(
                objective
            )
        )

        if hasattr(
            reasoning,
            "final_response",
        ):

            return (
                reasoning.final_response
            )

        return objective

    # ========================================================
    # EXECUTION ANALYTICS
    # ========================================================

    async def get_active_executions(
        self,
    ) -> List[
        SupervisorExecutionPlan
    ]:
        """
        Retrieve active executions.
        """

        async with self._lock:

            return list(
                self._active_executions.values()
            )

    # ========================================================
    # METRICS
    # ========================================================

    def _update_average_execution_time(
        self,
        execution_time: float,
    ) -> None:
        """
        Update supervisor metrics.
        """

        total = (
            self._metrics.successful_executions
        )

        if total <= 1:

            self._metrics.average_execution_time = (
                execution_time
            )

            return

        current = (
            self._metrics.average_execution_time
        )

        self._metrics.average_execution_time = (
            (
                current
                * (total - 1)
            )
            + execution_time
        ) / total

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    async def health_check(
        self,
    ) -> Dict[str, Any]:
        """
        Institutional diagnostics.
        """

        return {
            "status": "healthy",
            "active_executions": len(
                self._active_executions
            ),
            "successful_executions": (
                self._metrics.successful_executions
            ),
            "failed_executions": (
                self._metrics.failed_executions
            ),
            "recursive_plans_generated": (
                self._metrics.recursive_plans_generated
            ),
            "average_execution_time": (
                self._metrics.average_execution_time
            ),
        }

    # ========================================================
    # METRICS ACCESS
    # ========================================================

    def get_metrics(
        self,
    ) -> SupervisorMetrics:
        """
        Retrieve supervisor metrics.
        """

        return self._metrics
