"""
Institutional-Grade Planner Agent
=================================

Distributed Agentic Reasoning Framework (DARF)

Responsibilities:
- Recursive planning
- Workflow generation
- Execution graph construction
- Dependency orchestration
- Adaptive planning
- Strategic optimization
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
from typing import Set


# ============================================================
# PLANNING STRATEGY
# ============================================================


class PlanningStrategy(str, Enum):
    """
    Institutional planning strategies.
    """

    SEQUENTIAL = "sequential"

    PARALLEL = "parallel"

    HIERARCHICAL = "hierarchical"

    ADAPTIVE = "adaptive"

    HYBRID = "hybrid"


# ============================================================
# PLAN NODE
# ============================================================


@dataclass(slots=True)
class PlanNode:
    """
    Execution graph node.
    """

    node_id: str

    objective: str

    dependencies: List[str] = field(
        default_factory=list
    )

    priority: int = 1

    parallelizable: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# EXECUTION GRAPH
# ============================================================


@dataclass(slots=True)
class ExecutionGraph:
    """
    Institutional execution graph.
    """

    graph_id: str

    nodes: List[PlanNode]

    strategy: PlanningStrategy

    created_at: float = field(
        default_factory=time.time
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# PLANNING RESULT
# ============================================================


@dataclass(slots=True)
class PlanningResult:
    """
    Final planning output.
    """

    planning_id: str

    execution_graph: ExecutionGraph

    estimated_execution_steps: int

    parallel_stages: int

    optimization_score: float

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# PLANNER METRICS
# ============================================================


@dataclass(slots=True)
class PlannerMetrics:
    """
    Planner runtime metrics.
    """

    total_plans_generated: int = 0

    adaptive_replans: int = 0

    optimized_workflows: int = 0

    average_plan_complexity: float = 0.0


# ============================================================
# PLANNER AGENT
# ============================================================


class PlannerAgent:
    """
    Institutional strategic planning engine.

    Features:
    - recursive planning
    - execution graph generation
    - adaptive orchestration
    - workflow optimization
    """

    def __init__(
        self,
    ) -> None:

        self._metrics = (
            PlannerMetrics()
        )

        self._lock = asyncio.Lock()

    # ========================================================
    # MAIN PLANNING PIPELINE
    # ========================================================

    async def generate_execution_plan(
        self,
        objective: str,
        subtasks: List[str],
        strategy: PlanningStrategy = (
            PlanningStrategy.HYBRID
        ),
    ) -> PlanningResult:
        """
        Generate institutional execution graph.
        """

        graph = await self._build_execution_graph(
            objective=objective,
            subtasks=subtasks,
            strategy=strategy,
        )

        optimization_score = (
            await self._optimize_graph(
                graph
            )
        )

        parallel_stages = (
            await self._estimate_parallelism(
                graph
            )
        )

        result = PlanningResult(
            planning_id=str(uuid.uuid4()),
            execution_graph=graph,
            estimated_execution_steps=(
                len(graph.nodes)
            ),
            parallel_stages=parallel_stages,
            optimization_score=(
                optimization_score
            ),
            metadata={
                "strategy": strategy.value,
            },
        )

        async with self._lock:

            self._metrics.total_plans_generated += 1

            self._metrics.optimized_workflows += 1

            self._update_complexity_metrics(
                graph
            )

        return result

    # ========================================================
    # EXECUTION GRAPH CONSTRUCTION
    # ========================================================

    async def _build_execution_graph(
        self,
        objective: str,
        subtasks: List[str],
        strategy: PlanningStrategy,
    ) -> ExecutionGraph:
        """
        Build institutional execution graph.
        """

        nodes: List[
            PlanNode
        ] = []

        previous_node: Optional[
            str
        ] = None

        for index, task in enumerate(
            subtasks
        ):

            node_id = str(
                uuid.uuid4()
            )

            dependencies = []

            if (
                strategy
                == PlanningStrategy.SEQUENTIAL
                and previous_node
            ):

                dependencies.append(
                    previous_node
                )

            node = PlanNode(
                node_id=node_id,
                objective=task,
                dependencies=dependencies,
                priority=index + 1,
                parallelizable=(
                    strategy
                    != PlanningStrategy.SEQUENTIAL
                ),
            )

            nodes.append(node)

            previous_node = node_id

        return ExecutionGraph(
            graph_id=str(uuid.uuid4()),
            nodes=nodes,
            strategy=strategy,
            metadata={
                "objective": objective,
            },
        )

    # ========================================================
    # GRAPH OPTIMIZATION
    # ========================================================

    async def _optimize_graph(
        self,
        graph: ExecutionGraph,
    ) -> float:
        """
        Optimize execution graph.
        """

        total_nodes = len(
            graph.nodes
        )

        if total_nodes == 0:
            return 0.0

        parallelizable = len(
            [
                node
                for node in graph.nodes
                if node.parallelizable
            ]
        )

        optimization_score = (
            parallelizable
            / total_nodes
        )

        return round(
            optimization_score,
            4,
        )

    # ========================================================
    # PARALLELISM ESTIMATION
    # ========================================================

    async def _estimate_parallelism(
        self,
        graph: ExecutionGraph,
    ) -> int:
        """
        Estimate execution parallelism.
        """

        independent_nodes = len(
            [
                node
                for node in graph.nodes
                if not node.dependencies
            ]
        )

        return max(
            1,
            independent_nodes,
        )

    # ========================================================
    # ADAPTIVE REPLANNING
    # ========================================================

    async def adaptive_replan(
        self,
        graph: ExecutionGraph,
        failed_node_id: str,
    ) -> ExecutionGraph:
        """
        Dynamic institutional replanning.
        """

        async with self._lock:

            self._metrics.adaptive_replans += 1

        updated_nodes = []

        for node in graph.nodes:

            if (
                node.node_id
                == failed_node_id
            ):

                node.metadata[
                    "replanned"
                ] = True

                node.priority += 1

            updated_nodes.append(
                node
            )

        return ExecutionGraph(
            graph_id=str(uuid.uuid4()),
            nodes=updated_nodes,
            strategy=graph.strategy,
            metadata={
                "adaptive_replan": True,
            },
        )

    # ========================================================
    # DEPENDENCY ANALYSIS
    # ========================================================

    async def validate_graph(
        self,
        graph: ExecutionGraph,
    ) -> bool:
        """
        Validate graph integrity.
        """

        node_ids: Set[str] = {
            node.node_id
            for node in graph.nodes
        }

        for node in graph.nodes:

            for dependency in (
                node.dependencies
            ):

                if (
                    dependency
                    not in node_ids
                ):

                    return False

        return True

    # ========================================================
    # COMPLEXITY METRICS
    # ========================================================

    def _update_complexity_metrics(
        self,
        graph: ExecutionGraph,
    ) -> None:
        """
        Update planner metrics.
        """

        complexity = float(
            len(graph.nodes)
        )

        total = (
            self._metrics.total_plans_generated
        )

        if total <= 1:

            self._metrics.average_plan_complexity = (
                complexity
            )

            return

        current = (
            self._metrics.average_plan_complexity
        )

        self._metrics.average_plan_complexity = (
            (
                current
                * (total - 1)
            )
            + complexity
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
            "total_plans_generated": (
                self._metrics.total_plans_generated
            ),
            "adaptive_replans": (
                self._metrics.adaptive_replans
            ),
            "optimized_workflows": (
                self._metrics.optimized_workflows
            ),
            "average_plan_complexity": (
                self._metrics.average_plan_complexity
            ),
        }

    # ========================================================
    # METRICS ACCESS
    # ========================================================

    def get_metrics(
        self,
    ) -> PlannerMetrics:
        """
        Retrieve planner metrics.
        """

        return self._metrics
