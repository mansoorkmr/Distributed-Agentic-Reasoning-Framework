"""
Institutional-Grade Tool Execution Runtime
==========================================

Distributed Agentic Reasoning Framework (DARF)

Responsibilities:
- Async tool execution
- Runtime sandbox orchestration
- Timeout enforcement
- Retry management
- Failure recovery
- Execution monitoring
- Distributed-safe action runtime
"""

from __future__ import annotations

import asyncio
import time
import traceback
import uuid

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Dict
from typing import Optional

from agents.tools.registry.tool_registry import (
    RegisteredTool,
)
from agents.tools.registry.tool_registry import (
    ToolRegistry,
)
from agents.tools.registry.tool_registry import (
    ToolStatus,
)


# ============================================================
# EXECUTION STATUS
# ============================================================


class ExecutionStatus(str, Enum):
    """
    Tool execution lifecycle states.
    """

    PENDING = "pending"

    RUNNING = "running"

    SUCCESS = "success"

    FAILED = "failed"

    TIMEOUT = "timeout"

    RETRYING = "retrying"


# ============================================================
# EXECUTION CONTEXT
# ============================================================


@dataclass(slots=True)
class ExecutionContext:
    """
    Tool execution context.
    """

    execution_id: str

    tool_id: str

    started_at: float = field(
        default_factory=time.time
    )

    timeout_seconds: int = 30

    max_retries: int = 3

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# EXECUTION RESULT
# ============================================================


@dataclass(slots=True)
class ExecutionResult:
    """
    Tool execution result container.
    """

    execution_id: str

    tool_id: str

    status: ExecutionStatus

    result: Optional[Any] = None

    error: Optional[str] = None

    execution_time: Optional[
        float
    ] = None

    retries_used: int = 0

    traceback_info: Optional[
        str
    ] = None


# ============================================================
# EXECUTION STATS
# ============================================================


@dataclass(slots=True)
class ToolExecutorStats:
    """
    Tool execution statistics.
    """

    total_executions: int = 0

    successful_executions: int = 0

    failed_executions: int = 0

    timeout_failures: int = 0

    retry_operations: int = 0


# ============================================================
# TOOL EXECUTOR
# ============================================================


class ToolExecutor:
    """
    Institutional-grade tool execution runtime.

    Features:
    - Async-safe execution
    - Retry orchestration
    - Timeout enforcement
    - Failure recovery
    - Distributed execution support
    """

    def __init__(
        self,
        registry: ToolRegistry,
    ) -> None:

        self.registry = registry

        self._stats = ToolExecutorStats()

        self._lock = asyncio.Lock()

    # ========================================================
    # TOOL EXECUTION
    # ========================================================

    async def execute_tool(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        timeout_seconds: int = 30,
        max_retries: int = 3,
    ) -> ExecutionResult:
        """
        Execute registered tool.
        """

        execution_id = str(uuid.uuid4())

        started_at = time.time()

        tool = await self.registry.get_tool_by_name(
            tool_name
        )

        if not tool:

            return ExecutionResult(
                execution_id=execution_id,
                tool_id="unknown",
                status=ExecutionStatus.FAILED,
                error=f"Tool '{tool_name}' not found.",
            )

        if tool.status != ToolStatus.ACTIVE:

            return ExecutionResult(
                execution_id=execution_id,
                tool_id=tool.metadata.tool_id,
                status=ExecutionStatus.FAILED,
                error="Tool is not active.",
            )

        validation = await self.registry.validate_input(
            tool.metadata.tool_id,
            payload,
        )

        if not validation:

            return ExecutionResult(
                execution_id=execution_id,
                tool_id=tool.metadata.tool_id,
                status=ExecutionStatus.FAILED,
                error="Tool input validation failed.",
            )

        context = ExecutionContext(
            execution_id=execution_id,
            tool_id=tool.metadata.tool_id,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )

        result = await self._execute_with_retries(
            tool=tool,
            payload=payload,
            context=context,
        )

        result.execution_time = (
            time.time() - started_at
        )

        async with self._lock:

            self._stats.total_executions += 1

            if (
                result.status
                == ExecutionStatus.SUCCESS
            ):
                self._stats.successful_executions += 1

            elif (
                result.status
                == ExecutionStatus.TIMEOUT
            ):
                self._stats.timeout_failures += 1

            else:
                self._stats.failed_executions += 1

        return result

    # ========================================================
    # RETRY ORCHESTRATION
    # ========================================================

    async def _execute_with_retries(
        self,
        tool: RegisteredTool,
        payload: Dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Execute tool with retry logic.
        """

        retries = 0

        while retries <= context.max_retries:

            try:

                if retries > 0:

                    async with self._lock:

                        self._stats.retry_operations += 1

                result = await asyncio.wait_for(
                    tool.handler(**payload),
                    timeout=context.timeout_seconds,
                )

                await self.registry.track_execution(
                    tool.metadata.tool_id
                )

                return ExecutionResult(
                    execution_id=context.execution_id,
                    tool_id=tool.metadata.tool_id,
                    status=ExecutionStatus.SUCCESS,
                    result=result,
                    retries_used=retries,
                )

            except asyncio.TimeoutError:

                retries += 1

                if retries > context.max_retries:

                    return ExecutionResult(
                        execution_id=context.execution_id,
                        tool_id=tool.metadata.tool_id,
                        status=ExecutionStatus.TIMEOUT,
                        error="Execution timed out.",
                        retries_used=retries,
                    )

            except Exception as error:

                retries += 1

                if retries > context.max_retries:

                    return ExecutionResult(
                        execution_id=context.execution_id,
                        tool_id=tool.metadata.tool_id,
                        status=ExecutionStatus.FAILED,
                        error=str(error),
                        retries_used=retries,
                        traceback_info=traceback.format_exc(),
                    )

                await asyncio.sleep(1)

        return ExecutionResult(
            execution_id=context.execution_id,
            tool_id=tool.metadata.tool_id,
            status=ExecutionStatus.FAILED,
            error="Unknown execution failure.",
        )

    # ========================================================
    # PARALLEL EXECUTION
    # ========================================================

    async def execute_parallel(
        self,
        executions: list[
            tuple[
                str,
                Dict[str, Any],
            ]
        ],
    ) -> list[ExecutionResult]:
        """
        Execute tools in parallel.
        """

        tasks = [
            self.execute_tool(
                tool_name=name,
                payload=payload,
            )
            for name, payload
            in executions
        ]

        return await asyncio.gather(
            *tasks
        )

    # ========================================================
    # SANDBOX EXECUTION
    # ========================================================

    async def execute_sandboxed(
        self,
        tool_name: str,
        payload: Dict[str, Any],
    ) -> ExecutionResult:
        """
        Sandboxed execution wrapper.

        Future:
        - process isolation
        - container runtime
        - restricted execution
        """

        return await self.execute_tool(
            tool_name=tool_name,
            payload=payload,
        )

    # ========================================================
    # STATISTICS
    # ========================================================

    def get_stats(
        self,
    ) -> ToolExecutorStats:
        """
        Retrieve executor statistics.
        """

        return self._stats

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    async def health_check(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime health diagnostics.
        """

        return {
            "status": "healthy",
            "total_executions": (
                self._stats.total_executions
            ),
            "successful_executions": (
                self._stats.successful_executions
            ),
            "failed_executions": (
                self._stats.failed_executions
            ),
            "timeout_failures": (
                self._stats.timeout_failures
            ),
            "retry_operations": (
                self._stats.retry_operations
            ),
        }
