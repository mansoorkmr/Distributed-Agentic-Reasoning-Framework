"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Execution Plan

Purpose
-------
Defines the canonical execution plan used by the
DARF Execution Fabric.

An execution plan represents an immutable description
of the work that the execution engine must perform.

Responsibilities
----------------
- Execution description
- Task registration
- Execution metadata
- Policy attachment
- Resource description

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
from typing import Dict
from typing import List
from typing import Optional

import uuid

from execution.execution_policy import ExecutionPolicy
from execution.state_machine import ExecutionState

__all__ = [
    "ExecutionTask",
    "ExecutionPlan",
]



# ============================================================
# EXECUTION TASK
# ============================================================


@dataclass(slots=True)
class ExecutionTask:
    """
    Canonical execution task.

    Represents a single executable unit
    within an execution plan.
    """

    task_id: str = field(
        default_factory=lambda: (
            f"TASK-{uuid.uuid4().hex.upper()}"
        )
    )

    task_name: str = ""

    agent_id: Optional[str] = None

    callable_name: Optional[str] = None

    inputs: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    outputs: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    dependencies: List[
        str
    ] = field(
        default_factory=list
    )

    priority: int = 0
    
    state: ExecutionState = (
        ExecutionState.CREATED
    )

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"

    def __post_init__(
        self,
    ) -> None:
        """
        Validate execution task.
        """

        if not self.task_id:
            raise ValueError(
                "task_id cannot be empty."
            )

        if self.priority < 0:
            raise ValueError(
                "priority must be >= 0."
            )

        if self.dependencies is None:
            raise ValueError(
                "dependencies cannot be None."
            )

        if self.inputs is None:
            raise ValueError(
                "inputs cannot be None."
            )

        if self.outputs is None:
            raise ValueError(
                "outputs cannot be None."
            )


# ============================================================
# EXECUTION PLAN
# ============================================================


@dataclass(slots=True)
class ExecutionPlan:
    """
    Canonical execution plan.
    """

    plan_id: str = field(
        default_factory=lambda: (
            f"PLAN-{uuid.uuid4().hex.upper()}"
        )
    )

    execution_id: Optional[str] = None

    request_id: Optional[str] = None

    root_task: Optional[str] = None

    tasks: List[ExecutionTask] = field(
        default_factory=list
    )

    policy: ExecutionPolicy = field(
        default_factory=ExecutionPolicy
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    version: str = "1.0"

    def __post_init__(
        self,
    ) -> None:

        if self.tasks is None:
            raise ValueError(
                "tasks cannot be None."
            )
            # ========================================================
    # TASK MANAGEMENT
    # ========================================================

    def add_task(
        self,
        task: ExecutionTask,
    ) -> None:
        """
        Add a task to the execution plan.
        """

        if not isinstance(
            task,
            ExecutionTask,
        ):
            raise TypeError(
                "task must be an ExecutionTask."
            )

        if self.has_task(
            task.task_id,
        ):
            raise ValueError(
                f"Task '{task.task_id}' "
                f"already exists."
            )

        self.tasks.append(
            task,
        )

    def remove_task(
        self,
        task_id: str,
    ) -> None:
        """
        Remove a task from the plan.
        """

        task = self.get_task(
            task_id,
        )

        if task is None:
            raise ValueError(
                f"Unknown task '{task_id}'."
            )

        self.tasks.remove(
            task,
        )

    def get_task(
        self,
        task_id: str,
    ) -> Optional[
        ExecutionTask
    ]:
        """
        Return a task by ID.
        """

        for task in self.tasks:

            if (
                task.task_id
                == task_id
            ):
                return task

        return None

    def has_task(
        self,
        task_id: str,
    ) -> bool:
        """
        Determine whether a task
        exists.
        """

        return (
            self.get_task(
                task_id,
            )
            is not None
        )

    def task_count(
        self,
    ) -> int:
        """
        Return total number of tasks.
        """

        return len(
            self.tasks,
        )
        # ========================================================
    # VALIDATION
    # ========================================================

    def validate(
        self,
    ) -> None:
        """
        Validate execution plan consistency.

        Raises
        ------
        ValueError
            If the execution plan is invalid.
        """

        task_ids = set()

        for task in self.tasks:

            if task.task_id in task_ids:
                raise ValueError(
                    f"Duplicate task ID: "
                    f"{task.task_id}"
                )

            task_ids.add(
                task.task_id
            )

        for task in self.tasks:

            for dependency in task.dependencies:

                if dependency not in task_ids:

                    raise ValueError(
                        f"Task '{task.task_id}' "
                        f"depends on unknown "
                        f"task '{dependency}'."
                    )

        if (
            self.root_task is not None
            and self.root_task
            not in task_ids
        ):
            raise ValueError(
                "Root task does not exist "
                "in execution plan."
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
        Serialize the execution plan.
        """

        return {
            "plan_id": self.plan_id,
            "execution_id": self.execution_id,
            "request_id": self.request_id,
            "root_task": self.root_task,
            "tasks": [
                {
                    "task_id": task.task_id,
                    "task_name": task.task_name,
                    "agent_id": task.agent_id,
                    "callable_name": task.callable_name,
                    "inputs": task.inputs,
                    "outputs": task.outputs,
                    "dependencies": task.dependencies,
                    "priority": task.priority,
                    "state": task.state.value,
                    "metadata": task.metadata,
                    "version": task.version,
                }
                for task in self.tasks
            ],
            "policy": self.policy.to_dict(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(
        self,
    ) -> str:
        """
        Serialize the execution plan
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
            f"ExecutionPlan("
            f"{self.task_count()} tasks)"
        )

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"<ExecutionPlan "
            f"id='{self.plan_id}' "
            f"tasks={self.task_count()}>"
        )