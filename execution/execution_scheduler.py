"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Execution Scheduler

Purpose
-------
Defines the canonical execution scheduler used by the
DARF Execution Fabric.

Responsibilities
----------------
- Build execution graphs
- Validate execution plans
- Compute execution order
- Discover ready tasks
- Track completed tasks

Design Principles
-----------------
- Deterministic scheduling
- DAG-based execution
- Stateless scheduling
- Scheduler independent of workers

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

from typing import Set
from typing import List

from execution.execution_graph import ExecutionGraph
from execution.execution_plan import ExecutionPlan


__all__ = [
    "ExecutionScheduler",
]
# ============================================================
# EXECUTION SCHEDULER
# ============================================================


@dataclass(slots=True)
class ExecutionScheduler:
    """
    Canonical execution scheduler.
    """

    plan: ExecutionPlan

    graph: ExecutionGraph = field(
        init=False,
    )

    completed_tasks: Set[
        str
    ] = field(
        default_factory=set,
    )

    version: str = "1.0"

    def __post_init__(
        self,
    ) -> None:

        self.plan.validate()

        self.graph = ExecutionGraph(
            self.plan,
        )

        if self.graph.detect_cycle():

            raise ValueError(
                "Execution graph contains a cycle."
            )
    # ========================================================
    # SCHEDULER API
    # ========================================================

    def execution_order(
        self,
    ) -> List[str]:
        """
        Return the topological execution order.
        """

        return self.graph.topological_sort()

    def ready_tasks(
        self,
    ) -> List[str]:
        """
        Return tasks ready for execution.
        """

        return self.graph.ready_tasks(
            self.completed_tasks,
        )

    def mark_completed(
        self,
        task_id: str,
    ) -> None:
        """
        Mark a task as completed.
        """

        if not self.graph.get_task(task_id):
            raise ValueError(
                f"Unknown task '{task_id}'."
            )

        self.completed_tasks.add(
            task_id,
        )

    def remaining_tasks(
        self,
    ) -> List[str]:
        """
        Return remaining task IDs.
        """

        return [
            task_id
            for task_id in self.execution_order()
            if task_id not in self.completed_tasks
        ]

    def is_complete(
        self,
    ) -> bool:
        """
        Determine whether all tasks
        have completed.
        """

        return (
            len(self.completed_tasks)
            == self.graph.node_count()
        )
        # ========================================================
    # SCHEDULER STATISTICS
    # ========================================================

    def completed_count(
        self,
    ) -> int:
        """
        Return number of completed tasks.
        """

        return len(
            self.completed_tasks,
        )

    def remaining_count(
        self,
    ) -> int:
        """
        Return number of remaining tasks.
        """

        return (
            self.graph.node_count()
            - self.completed_count()
        )

    def progress(
        self,
    ) -> float:
        """
        Return execution progress
        between 0.0 and 1.0.
        """

        total = self.graph.node_count()

        if total == 0:
            return 1.0

        return (
            self.completed_count()
            / total
        )
        # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> dict:
        """
        Serialize scheduler state.
        """

        return {
            "execution_order":
                self.execution_order(),
            "completed_tasks":
                sorted(
                    self.completed_tasks,
                ),
            "remaining_tasks":
                self.remaining_tasks(),
            "progress":
                self.progress(),
            "completed":
                self.completed_count(),
            "remaining":
                self.remaining_count(),
            "is_complete":
                self.is_complete(),
            "version":
                self.version,
        }

    def to_json(
        self,
    ) -> str:
        """
        Serialize scheduler
        to JSON.
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
            f"ExecutionScheduler("
            f"{self.completed_count()}/"
            f"{self.graph.node_count()} completed)"
        )

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"<ExecutionScheduler "
            f"completed="
            f"{self.completed_count()} "
            f"remaining="
            f"{self.remaining_count()}>"
        )