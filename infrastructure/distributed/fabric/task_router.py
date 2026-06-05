"""
DARF Task Router
================

Distributed Agentic Reasoning Framework (DARF)

Responsibilities
----------------
- Distributed node selection
- Resource-aware routing
- Load-aware routing
- Route scoring
- Execution placement
- Routing observability
- Cluster execution decisions
"""

from __future__ import annotations

import asyncio
import time
import uuid

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional

from infrastructure.distributed.cluster_manager import (
    ClusterNode,
    NodeStatus,
)

from infrastructure.distributed.fabric.execution_context import (
    ExecutionContext,
)


# ============================================================
# ROUTING STRATEGY
# ============================================================


class RoutingStrategy(str, Enum):
    """
    Routing policies.
    """

    ROUND_ROBIN = "round_robin"

    LEAST_LOADED = "least_loaded"

    RESOURCE_AWARE = "resource_aware"

    LATENCY_AWARE = "latency_aware"

    CAPABILITY_AWARE = "capability_aware"

    HYBRID = "hybrid"


# ============================================================
# NODE SCORE
# ============================================================


@dataclass(slots=True)
class NodeScore:
    """
    Node evaluation result.
    """

    node_id: str

    total_score: float

    cpu_score: float

    gpu_score: float

    memory_score: float

    load_score: float

    capability_score: float


# ============================================================
# EXECUTION ROUTE
# ============================================================


@dataclass(slots=True)
class ExecutionRoute:
    """
    Final routing decision.
    """

    route_id: str

    task_id: str

    selected_node_id: str

    routing_strategy: str

    routing_score: float

    candidate_nodes: List[str]

    timestamp: float


# ============================================================
# ROUTING METRICS
# ============================================================


@dataclass(slots=True)
class RoutingMetrics:
    """
    Router telemetry.
    """

    total_routes: int = 0

    failed_routes: int = 0

    average_route_score: float = 0.0

    node_selections: Dict[str, int] = field(
        default_factory=dict
    )


# ============================================================
# TASK ROUTER
# ============================================================


class TaskRouter:
    """
    Distributed routing engine.

    Features
    --------
    - intelligent node selection
    - resource-aware routing
    - load balancing support
    - route history
    - routing observability
    """

    def __init__(self) -> None:

        self._route_history: List[
            ExecutionRoute
        ] = []

        self._metrics = RoutingMetrics()

        self._lock = asyncio.Lock()

        self._round_robin_index = 0

    # ========================================================
    # PUBLIC ROUTING API
    # ========================================================

    async def route_task(
        self,
        context: ExecutionContext,
        nodes: List[ClusterNode],
        strategy: RoutingStrategy = (
            RoutingStrategy.HYBRID
        ),
    ) -> ExecutionRoute:
        """
        Route task to optimal node.
        """

        active_nodes = [
            node
            for node in nodes
            if node.status
            == NodeStatus.ACTIVE
        ]

        if not active_nodes:

            async with self._lock:

                self._metrics.failed_routes += 1

            raise RuntimeError(
                "No active nodes available."
            )

        selected_node: ClusterNode

        route_score: float

        if (
            strategy
            == RoutingStrategy.ROUND_ROBIN
        ):

            selected_node = (
                self._select_round_robin(
                    active_nodes
                )
            )

            route_score = 1.0

        else:

            ranked = await self.rank_nodes(
                active_nodes
            )

            selected_node = next(
                node
                for node in active_nodes
                if node.node_id
                == ranked[0].node_id
            )

            route_score = (
                ranked[0].total_score
            )

        route = ExecutionRoute(
            route_id=str(uuid.uuid4()),
            task_id=context.task_id,
            selected_node_id=(
                selected_node.node_id
            ),
            routing_strategy=(
                strategy.value
            ),
            routing_score=route_score,
            candidate_nodes=[
                node.node_id
                for node in active_nodes
            ],
            timestamp=time.time(),
        )

        async with self._lock:

            self._route_history.append(
                route
            )

            self._metrics.total_routes += 1

            self._metrics.node_selections[
                selected_node.node_id
            ] = (
                self._metrics.node_selections.get(
                    selected_node.node_id,
                    0,
                )
                + 1
            )

            self._update_average_score(
                route_score
            )

        return route

    # ========================================================
    # ROUND ROBIN
    # ========================================================

    def _select_round_robin(
        self,
        nodes: List[ClusterNode],
    ) -> ClusterNode:

        index = (
            self._round_robin_index
            % len(nodes)
        )

        node = nodes[index]

        self._round_robin_index += 1

        return node

    # ========================================================
    # NODE RANKING
    # ========================================================

    async def rank_nodes(
        self,
        nodes: List[ClusterNode],
    ) -> List[NodeScore]:
        """
        Rank nodes by suitability.
        """

        scores = []

        for node in nodes:

            scores.append(
                self.score_node(node)
            )

        scores.sort(
            key=lambda x: x.total_score,
            reverse=True,
        )

        return scores

    # ========================================================
    # NODE SCORING
    # ========================================================

    def score_node(
        self,
        node: ClusterNode,
    ) -> NodeScore:
        """
        Compute routing score.
        """

        cpu_score = min(
            node.cpu_capacity / 100.0,
            1.0,
        )

        gpu_score = min(
            node.gpu_capacity / 100.0,
            1.0,
        )

        memory_score = min(
            node.memory_capacity_gb
            / 512.0,
            1.0,
        )

        load_score = max(
            0.0,
            1.0
            - (
                node.active_workloads
                / 100.0
            ),
        )

        capability_score = (
            cpu_score
            + gpu_score
            + memory_score
        ) / 3.0

        total_score = (
            cpu_score * 0.25
            + gpu_score * 0.25
            + memory_score * 0.20
            + load_score * 0.20
            + capability_score * 0.10
        )

        total_score = round(
            min(
                max(total_score, 0.0),
                1.0,
            ),
            4,
        )

        return NodeScore(
            node_id=node.node_id,
            total_score=total_score,
            cpu_score=round(
                cpu_score,
                4,
            ),
            gpu_score=round(
                gpu_score,
                4,
            ),
            memory_score=round(
                memory_score,
                4,
            ),
            load_score=round(
                load_score,
                4,
            ),
            capability_score=round(
                capability_score,
                4,
            ),
        )

    # ========================================================
    # HISTORY
    # ========================================================

    async def get_route_history(
        self,
    ) -> List[ExecutionRoute]:

        async with self._lock:

            return list(
                self._route_history
            )

    # ========================================================
    # METRICS
    # ========================================================

    def get_metrics(
        self,
    ) -> RoutingMetrics:

        return self._metrics

    def _update_average_score(
        self,
        score: float,
    ) -> None:

        total = (
            self._metrics.total_routes
        )

        if total <= 1:

            self._metrics.average_route_score = (
                score
            )

            return

        current = (
            self._metrics.average_route_score
        )

        self._metrics.average_route_score = (
            (
                current
                * (total - 1)
            )
            + score
        ) / total

    # ========================================================
    # HEALTH
    # ========================================================

    async def health_check(
        self,
    ) -> Dict[str, object]:

        return {
            "status": "healthy",
            "total_routes": (
                self._metrics.total_routes
            ),
            "failed_routes": (
                self._metrics.failed_routes
            ),
            "average_route_score": round(
                self._metrics.average_route_score,
                4,
            ),
            "tracked_nodes": len(
                self._metrics.node_selections
            ),
            "route_history_size": len(
                self._route_history
            ),
        }
