"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Dispatcher

Purpose
-------
Defines the canonical dispatcher used by the
DARF Execution Fabric.

Responsibilities
----------------
- Dispatch ready tasks
- Select execution workers
- Coordinate scheduler and workers
- Return execution results

Design Principles
-----------------
- Stateless dispatch
- Scheduler-driven
- Worker-independent
- Production-ready

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import itertools

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict
from typing import List
from typing import Callable

from execution.execution_scheduler import ExecutionScheduler
from execution.execution_worker import ExecutionWorker
from execution.execution_result import ExecutionResult
from execution.execution_plan import ExecutionTask

__all__ = [
    "Dispatcher",
]
# ============================================================
# DISPATCHER
# ============================================================


@dataclass(slots=True)
class Dispatcher:
    """
    Canonical execution dispatcher.
    """

    scheduler: ExecutionScheduler

    workers: List[
        ExecutionWorker
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

    _worker_cycle: Any = field(
        init=False,
        repr=False,
    )

    def __post_init__(
        self,
    ) -> None:

        if not self.workers:
            self.workers.append(
                ExecutionWorker()
            )

        self._worker_cycle = itertools.cycle(
            self.workers,
        )
            # ========================================================
    # WORKER SELECTION
    # ========================================================

    def next_worker(
        self,
    ) -> ExecutionWorker:
        """
        Return the next worker using
        round-robin scheduling.
        """

        return next(
            self._worker_cycle,
        )
        # ========================================================
    # TASK LOOKUP
    # ========================================================

    def get_task(
        self,
        task_id: str,
    ) -> ExecutionTask:
        """
        Return task by ID.
        """

        task = self.scheduler.graph.get_task(
            task_id,
        )

        if task is None:

            raise ValueError(
                f"Unknown task '{task_id}'."
            )

        return task
        # ========================================================
    # DISPATCH
    # ========================================================

    def dispatch(
        self,
        task_id: str,
        func: Callable[..., Any],
    ) -> ExecutionResult:
        """
        Dispatch a single task to the next available worker.
        """

        task = self.get_task(task_id)

        worker = self.next_worker()

        result = worker.execute(
            task,
            func,
        )

        if result.success:
            self.scheduler.mark_completed(
                task_id,
            )

        return result

    def dispatch_ready(
        self,
        callables: Dict[
            str,
            Callable[..., Any],
        ],
    ) -> List[
        ExecutionResult
    ]:
        """
        Dispatch every task that is currently ready.
        """

        results: List[
            ExecutionResult
        ] = []

        for task_id in self.scheduler.ready_tasks():

            task = self.get_task(task_id)

            if task.callable_name is None:

                raise ValueError(
                    f"Task '{task.task_name}' has no callable_name."
                )

            if task.callable_name not in callables:

                raise ValueError(
                    f"Callable '{task.callable_name}' not registered."
                )

            results.append(
                self.dispatch(
                    task_id,
                    callables[
                        task.callable_name
                    ],
                )
            )

        return results
        # ========================================================
    # WORKER STATISTICS
    # ========================================================

    def worker_count(
        self,
    ) -> int:
        """
        Return number of registered workers.
        """

        return len(
            self.workers,
        )

    def total_tasks_executed(
        self,
    ) -> int:
        """
        Return total executed tasks
        across all workers.
        """

        return sum(
            worker.tasks_executed
            for worker in self.workers
        )

    def total_tasks_failed(
        self,
    ) -> int:
        """
        Return total failed tasks
        across all workers.
        """

        return sum(
            worker.tasks_failed
            for worker in self.workers
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
        Serialize dispatcher state.
        """

        return {
            "workers": [
                worker.to_dict()
                for worker in self.workers
            ],
            "worker_count": self.worker_count(),
            "tasks_executed": self.total_tasks_executed(),
            "tasks_failed": self.total_tasks_failed(),
            "scheduler_complete": (
                self.scheduler.is_complete()
            ),
            "version": self.version,
        }

    def to_json(
        self,
    ) -> str:
        """
        Serialize dispatcher to JSON.
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
            f"Dispatcher("
            f"{self.worker_count()} workers)"
        )

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"<Dispatcher "
            f"workers={self.worker_count()} "
            f"executed={self.total_tasks_executed()}>"
        )