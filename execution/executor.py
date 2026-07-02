"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Executor

Purpose
-------
Defines the canonical executor used by the
DARF Execution Fabric.

Responsibilities
----------------
- Execute an execution plan
- Coordinate scheduler and dispatcher
- Collect execution results
- Return execution history

Design Principles
-----------------
- Single orchestration layer
- Scheduler-driven execution
- Dispatcher-based task execution
- Production-ready

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

from typing import Any
from typing import Callable
from typing import Dict
from typing import List

from execution.dispatcher import Dispatcher
from execution.execution_plan import ExecutionPlan
from execution.execution_result import ExecutionResult
from execution.execution_scheduler import ExecutionScheduler

__all__ = [
    "Executor",
]
# ============================================================
# EXECUTOR
# ============================================================


@dataclass(slots=True)
class Executor:
    """
    Canonical executor.
    """

    plan: ExecutionPlan

    scheduler: ExecutionScheduler = field(
        init=False,
    )

    dispatcher: Dispatcher = field(
        init=False,
    )

    results: List[
        ExecutionResult
    ] = field(
        default_factory=list,
    )

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict,
    )

    version: str = "1.0"

    def __post_init__(
        self,
    ) -> None:

        self.scheduler = ExecutionScheduler(
            self.plan,
        )

        self.dispatcher = Dispatcher(
            self.scheduler,
        )
            # ========================================================
    # EXECUTION
    # ========================================================

    def execute(
        self,
        callables: Dict[
            str,
            Callable[..., Any],
        ],
    ) -> List[
        ExecutionResult
    ]:
        """
        Execute the entire execution plan.
        """

        while not self.scheduler.is_complete():

            ready = self.scheduler.ready_tasks()

            if not ready:
                break

            batch = self.dispatcher.dispatch_ready(
                callables,
            )

            self.results.extend(
                batch,
            )

        return self.results
        # ========================================================
    # STATISTICS
    # ========================================================

    def execution_count(
        self,
    ) -> int:
        """
        Return total execution results.
        """

        return len(
            self.results,
        )

    def successful_results(
        self,
    ) -> List[ExecutionResult]:
        """
        Return successful execution results.
        """

        return [
            result
            for result in self.results
            if result.success
        ]

    def failed_results(
        self,
    ) -> List[ExecutionResult]:
        """
        Return failed execution results.
        """

        return [
            result
            for result in self.results
            if not result.success
        ]

    def success_count(
        self,
    ) -> int:
        """
        Return number of successful executions.
        """

        return len(
            self.successful_results(),
        )

    def failure_count(
        self,
    ) -> int:
        """
        Return number of failed executions.
        """

        return len(
            self.failed_results(),
        )

    def success_rate(
        self,
    ) -> float:
        """
        Return execution success rate.
        """

        total = self.execution_count()

        if total == 0:
            return 1.0

        return (
            self.success_count()
            / total
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
        """
        Serialize executor state.
        """

        return {
            "execution_count": self.execution_count(),
            "success_count": self.success_count(),
            "failure_count": self.failure_count(),
            "success_rate": self.success_rate(),
            "scheduler_complete": (
                self.scheduler.is_complete()
            ),
            "results": [
                result.to_dict()
                for result in self.results
            ],
            "version": self.version,
        }

    def to_json(
        self,
    ) -> str:
        """
        Serialize executor to JSON.
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
            f"Executor("
            f"{self.execution_count()} results)"
        )

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"<Executor "
            f"executions={self.execution_count()} "
            f"success={self.success_count()} "
            f"failed={self.failure_count()}>"
        )