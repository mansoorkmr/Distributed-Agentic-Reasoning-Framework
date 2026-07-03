"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Execution Orchestrator

Purpose
-------
Coordinates the complete execution lifecycle.

Responsibilities
----------------
- Execute execution plans
- Resolve dependencies
- Schedule tasks
- Execute agents
- Maintain execution history
- Update execution context

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from execution.execution_context import ExecutionContext
from execution.execution_history import ExecutionHistory, ExecutionRecord
from execution.execution_queue import ExecutionQueue
from execution.dependency_resolver import DependencyResolver
from execution.agent_executor import AgentExecutor
from execution.execution_plan import ExecutionPlan


__all__ = [
    "ExecutionOrchestrator",
]

# ============================================================
# EXECUTION ORCHESTRATOR
# ============================================================

@dataclass(slots=True)
class ExecutionOrchestrator:
    """
    Coordinates the complete execution pipeline.
    """

    context: ExecutionContext = field(
        default_factory=ExecutionContext,
    )

    history: ExecutionHistory = field(
        default_factory=ExecutionHistory,
    )

    queue: ExecutionQueue = field(
        default_factory=ExecutionQueue,
    )

    agent_executor: AgentExecutor = field(
        default_factory=AgentExecutor,
    )

    resolver: Optional[DependencyResolver] = field(
        default=None,
        init=False,
    )

    current_plan: Optional[ExecutionPlan] = field(
        default=None,
        init=False,
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict,
    )

    version: str = "1.0"

    def __post_init__(self) -> None:
        """
        Share the execution context
        with the AgentExecutor.
        """
        self.agent_executor.context = self.context

    # ============================================================
    # PLAN MANAGEMENT
    # ============================================================

    def load_plan(self, plan: ExecutionPlan) -> None:
        """
        Load an execution plan into the orchestrator.
        """
        if not isinstance(plan, ExecutionPlan):
            raise TypeError("plan must be an ExecutionPlan.")

        plan.validate()
        self.current_plan = plan
        self.resolver = DependencyResolver(plan)
        
        self.clear_queue()
        self.enqueue_tasks()

    def enqueue_tasks(self) -> None:
        """
        Enqueue every task in topological order.
        """
        if self.current_plan is None or self.resolver is None:
            return

        self.clear_queue()
        ordered = self.resolver.topological_order()

        for task_id in ordered:
            task = self.resolver.task(task_id)
            if task:
                self.queue.enqueue(task)

    def clear_queue(self) -> None:
        """
        Remove every queued task.
        """
        self.queue.clear()

    def has_plan(self) -> bool:
        """
        Determine whether an execution plan is loaded.
        """
        return self.current_plan is not None

    def task_count(self) -> int:
        """
        Return number of tasks in the loaded plan.
        """
        if self.current_plan is None:
            return 0
        return self.current_plan.task_count()

    # ============================================================
    # EXECUTION
    # ============================================================

    def execute(self, agents: Dict[str, Any]) -> None:
        """
        Execute the loaded execution plan.
        """
        if not self.has_plan():
            raise RuntimeError("No execution plan loaded.")

        while not self.queue.is_empty():
            task = self.queue.dequeue()
            
            if task is None:
                break

            if task.agent_id is None:
                raise ValueError(f"Task '{task.task_name}' has no agent_id.")

            if task.agent_id not in agents:
                raise ValueError(f"Unknown agent '{task.agent_id}'.")

            # Update context
            self.context.current_task = task.task_id

            # Execute the agent
            result = self.agent_executor.execute(
                agent=agents[task.agent_id],
                task=task,
            )

            # Explicitly map the ExecutionResult into an ExecutionRecord
            record = ExecutionRecord(
                task_id=task.task_id,
                task_name=task.task_name,
                success=result.success,
                status="completed" if result.success else "failed",
                duration=result.duration,
                output=result.output,
                error=result.error
            )

            # Add to history using the native add() method
            self.history.add(record)

    # ============================================================
    # STATISTICS
    # ============================================================

    def completed_tasks(self) -> int:
        """
        Return completed task count.
        """
        return self.history.completed_count()

    def failed_tasks(self) -> int:
        """
        Return failed task count.
        """
        return self.history.failure_count()

    def successful_tasks(self) -> int:
        """
        Return successful task count.
        """
        return self.history.success_count()

    def progress(self) -> float:
        """
        Return execution progress.
        """
        total = self.task_count()
        if total == 0:
            return 1.0
        return self.completed_tasks() / total

    # ============================================================
    # RESET
    # ============================================================

    def reset(self) -> None:
        """
        Reset the orchestrator.
        """
        self.context.reset()
        self.history.clear()
        self.queue.clear()
        self.current_plan = None
        self.resolver = None
        self.metadata.clear()

    # ============================================================
    # SERIALIZATION
    # ============================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize orchestrator state.
        """
        return {
            "has_plan": self.has_plan(),
            "task_count": self.task_count(),
            "progress": self.progress(),
            "completed_tasks": self.completed_tasks(),
            "successful_tasks": self.successful_tasks(),
            "failed_tasks": self.failed_tasks(),
            "context": self.context.to_dict(),
            "history": self.history.to_dict(),
            "queue": self.queue.to_dict(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        """
        Serialize orchestrator to JSON.
        """
        return json.dumps(
            self.to_dict(),
            indent=4,
            sort_keys=True,
            default=str
        )

    # ============================================================
    # REPRESENTATION
    # ============================================================

    def __str__(self) -> str:
        """
        Human-readable representation.
        """
        return f"ExecutionOrchestrator({self.task_count()} tasks)"

    def __repr__(self) -> str:
        """
        Developer representation.
        """
        return (
            f"<ExecutionOrchestrator "
            f"tasks={self.task_count()} "
            f"completed={self.completed_tasks()} "
            f"failed={self.failed_tasks()}>"
        )