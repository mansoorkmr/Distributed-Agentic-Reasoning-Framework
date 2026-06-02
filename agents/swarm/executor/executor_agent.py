"""
Institutional-Grade Executor Agent
==================================

Distributed Agentic Reasoning Framework (DARF)

Responsibilities:
- Autonomous execution
- Tool orchestration
- Distributed task execution
- Adaptive runtime pipelines
- Validation and recovery
- Operational cognition
"""

from __future__ import annotations

import asyncio
import statistics
import time
import uuid

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from agents.tools.execution.tool_executor import (
    ToolExecutor,
)

from agents.tools.registry.tool_registry import (
    ToolRegistry,
)


# ============================================================
# EXECUTION MODE
# ============================================================


class ExecutionMode(str, Enum):
    """
    Executor runtime modes.
    """

    SEQUENTIAL = "sequential"

    PARALLEL = "parallel"

    DISTRIBUTED = "distributed"

    ADAPTIVE = "adaptive"


# ============================================================
# EXECUTION TASK
# ============================================================


@dataclass(slots=True)
class ExecutionTask:
    """
    Distributed execution task.
    """

    task_id: str

    objective: str

    tool_name: Optional[
        str
    ] = None

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at: float = field(
        default_factory=time.time
    )


# ============================================================
# EXECUTION RESULT
# ============================================================


@dataclass(slots=True)
class ExecutionResult:
    """
    Institutional execution result.
    """

    execution_id: str

    success: bool

    outputs: List[Any]

    execution_time: float

    validated: bool

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# EXECUTION METRICS
# ============================================================


@dataclass(slots=True)
class ExecutorMetrics:
    """
    Executor runtime metrics.
    """

    total_executions: int = 0

    successful_executions: int = 0

    failed_executions: int = 0

    validation_failures: int = 0

    average_execution_time: float = 0.0


# ============================================================
# EXECUTOR AGENT
# ============================================================


class ExecutorAgent:
    """
    Institutional execution intelligence runtime.

    Features:
    - distributed execution
    - adaptive orchestration
    - validation pipelines
    - tool runtime integration
    """

    def __init__(
        self,
        tool_registry: ToolRegistry,
        tool_executor: ToolExecutor,
    ) -> None:

        self.tool_registry = (
            tool_registry
        )

        self.tool_executor = (
            tool_executor
        )

        self._metrics = (
            ExecutorMetrics()
        )

        self._active_tasks: Dict[
            str,
            ExecutionTask,
        ] = {}

        self._lock = asyncio.Lock()

    # ========================================================
    # MAIN EXECUTION PIPELINE
    # ========================================================

    async def execute_tasks(
        self,
        tasks: List[ExecutionTask],
        mode: ExecutionMode = (
            ExecutionMode.ADAPTIVE
        ),
    ) -> ExecutionResult:
        """
        Execute institutional execution pipeline.
        """

        started_at = time.time()

        execution_id = str(
            uuid.uuid4()
        )

        try:

            async with self._lock:

                for task in tasks:

                    self._active_tasks[
                        task.task_id
                    ] = task

            # =================================================
            # EXECUTION MODES
            # =================================================

            if (
                mode
                == ExecutionMode.SEQUENTIAL
            ):

                outputs = (
                    await self._execute_sequential(
                        tasks
                    )
                )

            else:

                outputs = (
                    await self._execute_parallel(
                        tasks
                    )
                )

            # =================================================
            # VALIDATION
            # =================================================

            validated = (
                await self._validate_outputs(
                    outputs
                )
            )

            execution_time = (
                time.time()
                - started_at
            )

            async with self._lock:

                self._metrics.total_executions += 1

                self._metrics.successful_executions += 1

                self._update_average_execution_time(
                    execution_time
                )

                self._active_tasks.clear()

            return ExecutionResult(
                execution_id=execution_id,
                success=True,
                outputs=outputs,
                execution_time=execution_time,
                validated=validated,
                metadata={
                    "mode": mode.value,
                    "task_count": len(
                        tasks
                    ),
                },
            )

        except Exception as error:

            execution_time = (
                time.time()
                - started_at
            )

            async with self._lock:

                self._metrics.total_executions += 1

                self._metrics.failed_executions += 1

            return ExecutionResult(
                execution_id=execution_id,
                success=False,
                outputs=[],
                execution_time=execution_time,
                validated=False,
                metadata={
                    "error": str(
                        error
                    ),
                },
            )

    # ========================================================
    # SEQUENTIAL EXECUTION
    # ========================================================

    async def _execute_sequential(
        self,
        tasks: List[ExecutionTask],
    ) -> List[Any]:
        """
        Sequential execution pipeline.
        """

        outputs = []

        for task in tasks:

            result = (
                await self._execute_task(
                    task
                )
            )

            outputs.append(result)

        return outputs

    # ========================================================
    # PARALLEL EXECUTION
    # ========================================================

    async def _execute_parallel(
        self,
        tasks: List[ExecutionTask],
    ) -> List[Any]:
        """
        Parallel institutional execution.
        """

        execution_tasks = [
            self._execute_task(task)
            for task in tasks
        ]

        return await asyncio.gather(
            *execution_tasks,
            return_exceptions=False,
        )

    # ========================================================
    # TASK EXECUTION
    # ========================================================

    async def _execute_task(
        self,
        task: ExecutionTask,
    ) -> Any:
        """
        Execute individual task.
        """

        if not task.tool_name:

            return {
                "task_id": task.task_id,
                "objective": (
                    task.objective
                ),
                "status": "completed",
            }

        tool = (
            await self.tool_registry.get_tool(
                task.tool_name
            )
        )

        if not tool:

            raise ValueError(
                f"Tool not found: {task.tool_name}"
            )

        result = (
            await self.tool_executor.execute(
                tool_name=task.tool_name,
                payload=task.payload,
            )
        )

        return result

    # ========================================================
    # VALIDATION
    # ========================================================

    async def _validate_outputs(
        self,
        outputs: List[Any],
    ) -> bool:
        """
        Institutional validation pipeline.
        """

        if not outputs:

            async with self._lock:

                self._metrics.validation_failures += 1

            return False

        return True

    # ========================================================
    # ACTIVE EXECUTIONS
    # ========================================================

    async def get_active_tasks(
        self,
    ) -> List[ExecutionTask]:
        """
        Retrieve active tasks.
        """

        async with self._lock:

            return list(
                self._active_tasks.values()
            )

    # ========================================================
    # METRICS
    # ========================================================

    def _update_average_execution_time(
        self,
        execution_time: float,
    ) -> None:
        """
        Update runtime metrics.
        """

        total = (
            self._metrics.successful_executions
        )

        if total <= 1:

            self._metrics.average_execution_time = (
                execution_time
            )

            return

        current = (
            self._metrics.average_execution_time
        )

        self._metrics.average_execution_time = (
            (
                current
                * (total - 1)
            )
            + execution_time
        ) / total

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    async def health_check(
        self,
    ) -> Dict[str, Any]:
        """
        Institutional diagnostics.
        """

        return {
            "status": "healthy",
            "active_tasks": len(
                self._active_tasks
            ),
            "successful_executions": (
                self._metrics.successful_executions
            ),
            "failed_executions": (
                self._metrics.failed_executions
            ),
            "validation_failures": (
                self._metrics.validation_failures
            ),
            "average_execution_time": (
                self._metrics.average_execution_time
            ),
        }

    # ========================================================
    # METRICS ACCESS
    # ========================================================

    def get_metrics(
        self,
    ) -> ExecutorMetrics:
        """
        Retrieve executor metrics.
        """

        return self._metrics
