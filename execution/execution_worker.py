"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Execution Worker

Purpose
-------
Defines the canonical execution worker used by the
DARF Execution Fabric.

Responsibilities
----------------
- Execute a single execution task
- Capture execution results
- Convert exceptions into execution results
- Remain scheduler-independent

Design Principles
-----------------
- Single responsibility
- Stateless execution
- Exception-safe
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

from execution.execution_plan import ExecutionTask
from execution.execution_result import ExecutionResult
from execution.exceptions import DARFExecutionError


__all__ = [
    "ExecutionWorker",
]

# ============================================================
# EXECUTION WORKER
# ============================================================

@dataclass(slots=True)
class ExecutionWorker:
    """
    Canonical execution worker.
    """

    worker_id: str = "worker"

    tasks_executed: int = 0

    tasks_failed: int = 0

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict,
    )

    version: str = "1.0"

    # ========================================================
    # EXECUTION
    # ========================================================

    def execute(
        self,
        task: ExecutionTask,
        func: Callable[..., Any],
    ) -> ExecutionResult:
        """
        Execute a single task.
        """

        result = ExecutionResult(
            task_name=task.task_name,
            agent_id=task.agent_id,
        )

        result.mark_started()

        self.tasks_executed += 1

        try:

            value = func(
                **task.inputs,
            )

            result.mark_completed(
                result=value,
            )

            task.outputs = {
                "result": value,
            }

            return result

        except DARFExecutionError as exc:

            self.tasks_failed += 1

            return ExecutionResult.from_exception(
                exc,
            )

        except Exception as exc:

            self.tasks_failed += 1

            wrapped = DARFExecutionError.from_exception(
                exc,
            )

            return ExecutionResult.from_exception(
                wrapped,
            )

    # ========================================================
    # STATISTICS
    # ========================================================

    def successful_tasks(
        self,
    ) -> int:
        """
        Return successful executions.
        """

        return (
            self.tasks_executed
            - self.tasks_failed
        )

    def failure_rate(
        self,
    ) -> float:
        """
        Return failure rate.
        """

        if self.tasks_executed == 0:
            return 0.0

        return (
            self.tasks_failed
            / self.tasks_executed
        )

    def success_rate(
        self,
    ) -> float:
        """
        Return success rate.
        """

        if self.tasks_executed == 0:
            return 1.0

        return (
            self.successful_tasks()
            / self.tasks_executed
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
            "worker_id": self.worker_id,
            "tasks_executed": self.tasks_executed,
            "tasks_failed": self.tasks_failed,
            "tasks_succeeded": self.successful_tasks(),
            "success_rate": self.success_rate(),
            "failure_rate": self.failure_rate(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(
        self,
    ) -> str:

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

        return (
            f"Worker("
            f"{self.tasks_executed} tasks)"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<ExecutionWorker "
            f"id='{self.worker_id}' "
            f"executed={self.tasks_executed} "
            f"failed={self.tasks_failed}>"
        )