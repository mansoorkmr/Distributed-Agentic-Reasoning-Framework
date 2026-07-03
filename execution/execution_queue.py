"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Execution Queue

Purpose
-------
Defines the canonical execution queue used by the
DARF Execution Fabric.

The execution queue is responsible for storing tasks
that are waiting to be executed by the execution
workers.

Responsibilities
----------------
- FIFO task queue
- Task insertion
- Task removal
- Queue inspection
- Queue statistics
- Serialization

Design Principles
-----------------
- Simple FIFO queue
- Deterministic ordering
- Thread-safe ready
- Production-ready

Thread Safety
-------------
Currently single-threaded.
Can be upgraded using locks without changing
the public API.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, Optional

from execution.execution_plan import ExecutionTask


__all__ = [
    "ExecutionQueue",
]


# ============================================================
# EXECUTION QUEUE
# ============================================================


@dataclass(slots=True)
class ExecutionQueue:
    """
    Canonical FIFO execution queue.

    Stores execution tasks before they are executed
    by execution workers.
    """

    queue: Deque[ExecutionTask] = field(
        default_factory=deque,
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict,
    )

    version: str = "1.0"

    # ========================================================
    # QUEUE OPERATIONS
    # ========================================================

    def enqueue(
        self,
        task: ExecutionTask,
    ) -> bool:
        """
        Add an execution task to the queue.

        Parameters
        ----------
        task : ExecutionTask
            Task to enqueue.

        Returns
        -------
        bool
            True if successfully added.
        """
        if not isinstance(task, ExecutionTask):
            raise TypeError("task must be an ExecutionTask.")

        self.queue.append(task)
        return True

    def dequeue(self) -> Optional[ExecutionTask]:
        """
        Remove and return the next task.

        Returns
        -------
        ExecutionTask | None
        """
        if self.is_empty():
            return None

        return self.queue.popleft()

    def peek(self) -> Optional[ExecutionTask]:
        """
        Return the next task without removing it.
        """
        if self.is_empty():
            return None

        return self.queue[0]

    # ========================================================
    # SEARCH
    # ========================================================

    def contains(
        self,
        task_id: str,
    ) -> bool:
        """
        Determine whether a task exists in the queue.

        Parameters
        ----------
        task_id : str
            Execution task ID.

        Returns
        -------
        bool
        """
        return self.get(task_id) is not None

    def get(
        self,
        task_id: str,
    ) -> Optional[ExecutionTask]:
        """
        Return a task by ID.

        Parameters
        ----------
        task_id : str

        Returns
        -------
        ExecutionTask | None
        """
        for task in self.queue:
            if task.task_id == task_id:
                return task
        return None

    def remove(
        self,
        task_id: str,
    ) -> bool:
        """
        Remove a task from the queue.

        Parameters
        ----------
        task_id : str

        Returns
        -------
        bool
            True if removed.
            False if not found.
        """
        task = self.get(task_id)

        if task is None:
            return False

        self.queue.remove(task)
        return True

    # ========================================================
    # QUEUE STATE
    # ========================================================

    def clear(self) -> None:
        """
        Remove every task from the queue.
        """
        self.queue.clear()

    def is_empty(self) -> bool:
        """
        Determine whether the queue is empty.
        """
        return len(self.queue) == 0

    def size(self) -> int:
        """
        Return the number of queued tasks.
        """
        return len(self.queue)

    def tasks(self) -> list[ExecutionTask]:
        """
        Return all queued tasks.

        Returns
        -------
        list[ExecutionTask]
            Snapshot of the queue.
        """
        return list(self.queue)

    def task_ids(self) -> list[str]:
        """
        Return queued task IDs.

        Returns
        -------
        list[str]
        """
        return [task.task_id for task in self.queue]

    def front(self) -> Optional[ExecutionTask]:
        """
        Alias for peek().
        """
        return self.peek()

    def back(self) -> Optional[ExecutionTask]:
        """
        Return the last queued task.
        """
        if self.is_empty():
            return None

        return self.queue[-1]

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the execution queue.
        """
        return {
            "size": self.size(),
            "tasks": [
                {
                    "task_id": task.task_id,
                    "task_name": task.task_name,
                    "agent_id": task.agent_id,
                    "callable_name": task.callable_name,
                    "priority": task.priority,
                    "state": task.state.value,
                    "dependencies": list(task.dependencies),
                    "metadata": task.metadata,
                    "version": task.version,
                }
                for task in self.queue
            ],
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        """
        Serialize the execution queue to JSON.
        """
        return json.dumps(
            self.to_dict(),
            indent=4,
            sort_keys=True,
        )

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __len__(self) -> int:
        """
        Return queue size.
        """
        return self.size()

    def __iter__(self):
        """
        Iterate over queued tasks.
        """
        return iter(self.queue)

    def __contains__(
        self,
        task_id: str,
    ) -> bool:
        """
        Membership operator.
        """
        return self.contains(task_id)

    def __str__(self) -> str:
        """
        Human-readable representation.
        """
        return f"ExecutionQueue({self.size()} tasks)"

    def __repr__(self) -> str:
        """
        Developer representation.
        """
        return f"<ExecutionQueue size={self.size()}>"