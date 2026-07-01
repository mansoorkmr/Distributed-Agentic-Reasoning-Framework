"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Execution Graph

Purpose
-------
Defines the canonical execution dependency graph used by the
DARF Execution Fabric.

The execution graph transforms an execution plan into
a Directed Acyclic Graph (DAG).

Responsibilities
----------------
- Task dependency graph
- Parent-child relationships
- Graph validation
- DAG construction
- Scheduler support

Design Principles
-----------------
- Directed acyclic graph
- Immutable task identity
- Efficient traversal
- Scheduler-friendly
- Distributed execution ready

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from typing import Dict
from typing import List
from typing import Set

from execution.execution_plan import ExecutionPlan
from execution.execution_plan import ExecutionTask


__all__ = [
    "ExecutionGraph",
]


# ============================================================
# EXECUTION GRAPH
# ============================================================


@dataclass(slots=True)
class ExecutionGraph:
    """
    Canonical execution dependency graph.
    """

    plan: ExecutionPlan

    adjacency: Dict[
        str,
        Set[str],
    ] = field(
        default_factory=dict
    )

    reverse_adjacency: Dict[
        str,
        Set[str],
    ] = field(
        default_factory=dict
    )

    task_index: Dict[
        str,
        ExecutionTask,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"

    def __post_init__(
        self,
    ) -> None:
        """
        Build the dependency graph.
        """

        self._build_graph()

    # ========================================================
    # GRAPH CONSTRUCTION
    # ========================================================

    def _build_graph(
        self,
    ) -> None:
        """
        Construct adjacency lists.
        """

        # Build the task index
        for task in self.plan.tasks:
            self.task_index[
                task.task_id
            ] = task

        for task in self.plan.tasks:

            self.adjacency.setdefault(
                task.task_id,
                set(),
            )

            self.reverse_adjacency.setdefault(
                task.task_id,
                set(),
            )

        for task in self.plan.tasks:

            for dependency in task.dependencies:

                self.adjacency[
                    dependency
                ].add(
                    task.task_id,
                )

                self.reverse_adjacency[
                    task.task_id
                ].add(
                    dependency,
                )

    # ========================================================
    # GRAPH QUERIES
    # ========================================================

    def get_task(
        self,
        task_id: str,
    ) -> ExecutionTask | None:
        """
        Return a task by ID.
        """

        return self.task_index.get(
            task_id,
        )

    def successors(
        self,
        task_id: str,
    ) -> Set[str]:
        """
        Return all successor tasks.
        """

        return self.adjacency.get(
            task_id,
            set(),
        )

    def predecessors(
        self,
        task_id: str,
    ) -> Set[str]:
        """
        Return all predecessor tasks.
        """

        return self.reverse_adjacency.get(
            task_id,
            set(),
        )

    def roots(
        self,
    ) -> List[str]:
        """
        Return all root tasks.
        """

        return [
            task_id
            for task_id, parents
            in self.reverse_adjacency.items()
            if not parents
        ]

    def leaves(
        self,
    ) -> List[str]:
        """
        Return all leaf tasks.
        """

        return [
            task_id
            for task_id, children
            in self.adjacency.items()
            if not children
        ]

    # ========================================================
    # GRAPH VALIDATION
    # ========================================================

    def detect_cycle(
        self,
    ) -> bool:
        """
        Determine whether the execution
        graph contains a cycle.

        Returns
        -------
        bool
            True if a cycle exists,
            otherwise False.
        """

        visited: Set[str] = set()

        visiting: Set[str] = set()

        def dfs(
            node: str,
        ) -> bool:

            if node in visiting:
                return True

            if node in visited:
                return False

            visiting.add(
                node,
            )

            for successor in self.successors(
                node,
            ):

                if dfs(
                    successor,
                ):
                    return True

            visiting.remove(
                node,
            )

            visited.add(
                node,
            )

            return False

        for node in self.adjacency:

            if dfs(
                node,
            ):
                return True

        return False

    # ========================================================
    # TOPOLOGICAL SORT
    # ========================================================

    def topological_sort(
        self,
    ) -> List[str]:
        """
        Return a topological ordering
        of the execution graph.

        Raises
        ------
        ValueError
            If the graph contains
            a cycle.
        """

        from collections import deque

        indegree: Dict[
            str,
            int,
        ] = {
            node: len(
                self.predecessors(
                    node,
                )
            )
            for node in self.adjacency
        }

        queue = deque(
            node
            for node, degree
            in indegree.items()
            if degree == 0
        )

        ordering: List[
            str
        ] = []

        while queue:

            node = queue.popleft()

            ordering.append(
                node,
            )

            for successor in self.successors(
                node,
            ):

                indegree[
                    successor
                ] -= 1

                if (
                    indegree[
                        successor
                    ] == 0
                ):
                    queue.append(
                        successor,
                    )

        if (
            len(ordering)
            != len(
                self.adjacency
            )
        ):
            raise ValueError(
                "Execution graph "
                "contains a cycle."
            )

        return ordering

    # ========================================================
    # SCHEDULER SUPPORT
    # ========================================================

    def ready_tasks(
        self,
        completed: Set[str],
    ) -> List[str]:
        """
        Return tasks whose dependencies
        have all been satisfied.
        """

        ready: List[str] = []

        for task_id in self.topological_sort():

            if task_id in completed:
                continue

            if all(
                dependency in completed
                for dependency in self.predecessors(
                    task_id,
                )
            ):
                ready.append(
                    task_id,
                )

        return ready

    # ========================================================
    # GRAPH STATISTICS
    # ========================================================

    def node_count(
        self,
    ) -> int:
        """
        Return total number of nodes.
        """

        return len(
            self.adjacency,
        )

    def edge_count(
        self,
    ) -> int:
        """
        Return total number of edges.
        """

        return sum(
            len(children)
            for children
            in self.adjacency.values()
        )

    def is_empty(
        self,
    ) -> bool:
        """
        Determine whether the graph
        contains any nodes.
        """

        return (
            self.node_count()
            == 0
        )

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, object]:
        """
        Serialize the execution graph.
        """

        return {
            "plan_id": self.plan.plan_id,
            "nodes": self.node_count(),
            "edges": self.edge_count(),
            "adjacency": {
                node: sorted(children)
                for node, children in self.adjacency.items()
            },
            "reverse_adjacency": {
                node: sorted(parents)
                for node, parents in self.reverse_adjacency.items()
            },
            "version": self.version,
        }

    def to_json(
        self,
    ) -> str:
        """
        Serialize the execution graph to JSON.
        """

        import json

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
        """
        Human-readable representation.
        """

        return (
            f"ExecutionGraph("
            f"{self.node_count()} nodes, "
            f"{self.edge_count()} edges)"
        )

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"<ExecutionGraph "
            f"nodes={self.node_count()} "
            f"edges={self.edge_count()}>"
        )