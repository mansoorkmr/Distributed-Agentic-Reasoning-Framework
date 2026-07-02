"""
Distributed Agentic Reasoning Framework (DARF)
Planner

Planning Graph

Purpose
-------
Defines the canonical planning graph used by the
DARF Planner.

The planning graph represents task dependencies
during planning before execution.

Responsibilities
----------------
- Build dependency graph
- Discover roots
- Discover leaves
- Detect cycles
- Topological ordering

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
from typing import Set

from execution.execution_plan import ExecutionPlan

__all__ = [
    "PlanningGraph",
]
# ============================================================
# PLANNING GRAPH
# ============================================================


@dataclass(slots=True)
class PlanningGraph:
    """
    Canonical planning graph.
    """

    plan: ExecutionPlan

    adjacency: Dict[
        str,
        Set[str],
    ] = field(
        init=False,
    )

    reverse_adjacency: Dict[
        str,
        Set[str],
    ] = field(
        init=False,
    )

    version: str = "1.0"
        # ========================================================
    # INITIALIZATION
    # ========================================================

    def __post_init__(
        self,
    ) -> None:

        self.adjacency = {}
        self.reverse_adjacency = {}

        self._build_graph()

    def _build_graph(
        self,
    ) -> None:

        for task in self.plan.tasks:

            self.adjacency[
                task.task_id
            ] = set()

            self.reverse_adjacency[
                task.task_id
            ] = set()

        for task in self.plan.tasks:

            for dependency in task.dependencies:

                self.adjacency[
                    dependency
                ].add(
                    task.task_id
                )

                self.reverse_adjacency[
                    task.task_id
                ].add(
                    dependency
                )
                    # ========================================================
    # HELPERS
    # ========================================================

    def roots(
        self,
    ) -> List[str]:

        return [
            node
            for node, deps
            in self.reverse_adjacency.items()
            if not deps
        ]

    def leaves(
        self,
    ) -> List[str]:

        return [
            node
            for node, children
            in self.adjacency.items()
            if not children
        ]

    def node_count(
        self,
    ) -> int:

        return len(
            self.adjacency
        )

    def edge_count(
        self,
    ) -> int:

        return sum(
            len(edges)
            for edges
            in self.adjacency.values()
        )
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
            "plan_id": self.plan.plan_id,
            "nodes": self.node_count(),
            "edges": self.edge_count(),
            "adjacency": {
                node: sorted(edges)
                for node, edges
                in self.adjacency.items()
            },
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
            f"PlanningGraph("
            f"{self.node_count()} nodes, "
            f"{self.edge_count()} edges)"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<PlanningGraph "
            f"nodes={self.node_count()} "
            f"edges={self.edge_count()}>"
        )