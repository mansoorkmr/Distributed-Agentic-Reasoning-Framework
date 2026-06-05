"""
DARF Execution Fabric
=====================

Distributed Agentic Reasoning Framework

Responsibilities
----------------
- Distributed execution orchestration
- Execution lifecycle management
- Queue coordination
- Routing coordination
- Resource allocation coordination
- Retry handling
- Failure handling
- Runtime metrics
"""

from __future__ import annotations

import asyncio
import time
import uuid

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Dict
from typing import Optional

from infrastructure.distributed.fabric.execution_context import (
    ExecutionContext,
    ExecutionMode,
)

from infrastructure.distributed.fabric.execution_queue import (
    ExecutionQueue,
    QueuePriority,
)

from infrastructure.distributed.fabric.task_router import (
    TaskRouter,
    RoutingStrategy,
)

from infrastructure.distributed.fabric.workload_allocator import (
    WorkloadAllocator,
    ResourceRequest,
)


# ============================================================
# FABRIC STATUS
# ============================================================


class FabricStatus(str, Enum):

    STARTING = "starting"

    RUNNING = "running"

    DEGRADED = "degraded"

    STOPPING = "stopping"

    STOPPED = "stopped"


# ============================================================
# FABRIC TASK
# ============================================================


@dataclass(slots=True)
class FabricTask:

    task_id: str

    agent_id: str

    payload: Dict[str, Any]

    priority: QueuePriority

    resource_request: ResourceRequest


# ============================================================
# FABRIC METRICS
# ============================================================


@dataclass(slots=True)
class FabricMetrics:

    submitted_tasks: int = 0

    completed_tasks: int = 0

    failed_tasks: int = 0

    active_tasks: int = 0

    allocation_failures: int = 0

    routing_failures: int = 0

    execution_failures: int = 0

    retry_count: int = 0

    average_execution_time_ms: float = 0.0


# ============================================================
# EXECUTION FABRIC
# ============================================================


class ExecutionFabric:
    """
    Central distributed execution runtime.

    Coordinates:

    Queue
      ↓
    Router
      ↓
    Allocator
      ↓
    Execution
    """

    DEFAULT_MAX_RETRIES = 3

    def __init__(
        self,
        queue: Optional[ExecutionQueue] = None,
        router: Optional[TaskRouter] = None,
        allocator: Optional[WorkloadAllocator] = None,
    ) -> None:

        self.queue = queue or ExecutionQueue()

        self.router = router or TaskRouter()

        self.allocator = (
            allocator or WorkloadAllocator()
        )

        self.status = FabricStatus.STOPPED

        self.metrics = FabricMetrics()

        self.active_executions: Dict[
            str,
            ExecutionContext,
        ] = {}

        self._lock = asyncio.Lock()

    # ========================================================
    # LIFECYCLE
    # ========================================================

    async def start(self) -> None:

        async with self._lock:

            self.status = FabricStatus.STARTING

            self.status = FabricStatus.RUNNING

    async def stop(self) -> None:

        async with self._lock:

            self.status = FabricStatus.STOPPING

            self.status = FabricStatus.STOPPED

    # ========================================================
    # SUBMIT
    # ========================================================

    async def submit_task(
        self,
        task_id: str,
        agent_id: str,
        payload: Dict[str, Any],
        resource_request: ResourceRequest,
        priority: QueuePriority = (
            QueuePriority.NORMAL
        ),
        mode: ExecutionMode = (
            ExecutionMode.DISTRIBUTED
        ),
    ) -> str:

        if self.status != FabricStatus.RUNNING:

            raise RuntimeError(
                "Execution fabric not running."
            )

        context = ExecutionContext(
            task_id=task_id,
            agent_id=agent_id,
            mode=mode,
        )

        task = FabricTask(
            task_id=task_id,
            agent_id=agent_id,
            payload=payload,
            priority=priority,
            resource_request=resource_request,
        )

        await context.mark_queued()

        await self.queue.enqueue(
            context=context,
            payload={
                "fabric_task": task,
            },
            priority=priority,
        )

        async with self._lock:

            self.metrics.submitted_tasks += 1

        return context.execution_id

    # ========================================================
    # SCHEDULER
    # ========================================================

    async def process_next(
        self,
        nodes: list,
    ) -> Optional[Any]:

        if self.status != FabricStatus.RUNNING:
            return None

        item = await self.queue.dequeue()

        if item is None:
            return None

        context = item.context

        task: FabricTask = item.payload[
            "fabric_task"
        ]

        try:

            await context.mark_routed()

            route = (
                await self.router.route_task(
                    context=context,
                    nodes=nodes,
                    strategy=RoutingStrategy.HYBRID,
                )
            )

        except Exception:

            async with self._lock:

                self.metrics.routing_failures += 1

            await self.fail(
                context,
                "routing_failure",
            )

            return None

        try:

            allocation = (
                await self.allocator.allocate(
                    task.resource_request
                )
            )

            #
            # Resource allocation successful
            #
            # ROUTED -> SCHEDULED
            #

            await context.mark_scheduled()

        except Exception:

            async with self._lock:

                self.metrics.allocation_failures += 1

            await self.fail(
                context,
                "allocation_failure",
            )

            return None

        return await self.execute(
            context=context,
            route=route,
            allocation=allocation,
            task=task,
        )
    # ========================================================
    # EXECUTION
    # ========================================================

    async def execute(
        self,
        context: ExecutionContext,
        route: Any,
        allocation: Any,
        task: FabricTask,
    ) -> Dict[str, Any]:

        start_time = time.time()

        await context.mark_running()

        self.active_executions[
            context.execution_id
        ] = context

        async with self._lock:

            self.metrics.active_tasks += 1

        try:

            #
            # Future integration point:
            #
            # Agent Runtime
            # Reasoning Engine
            # Tool Executor
            # RAG Pipeline
            #

            result = {
                "status": "success",
                "task_id": task.task_id,
                "agent_id": task.agent_id,
                "execution_id": (
                    context.execution_id
                ),
                "route": getattr(
                    route,
                    "selected_node_id",
                    None,
                ),
            }

            await self.complete(
                context=context,
                allocation=allocation,
                result=result,
                execution_start=start_time,
            )

            return result

        except Exception as exc:

            await self.fail(
                context=context,
                reason=str(exc),
                allocation=allocation,
            )

            raise

    # ========================================================
    # COMPLETE
    # ========================================================

    async def complete(
        self,
        context: ExecutionContext,
        allocation: Any,
        result: Dict[str, Any],
        execution_start: float,
    ) -> None:

        await context.mark_completed(
            output=result
        )

        elapsed_ms = (
            time.time() - execution_start
        ) * 1000

        try:

            await self.allocator.release(
                allocation.allocation_id
            )

        except Exception:
            pass

        self.active_executions.pop(
            context.execution_id,
            None,
        )

        async with self._lock:

            self.metrics.completed_tasks += 1

            self.metrics.active_tasks = max(
                0,
                self.metrics.active_tasks - 1,
            )

            self._update_average_execution(
                elapsed_ms
            )

    # ========================================================
    # FAIL
    # ========================================================

    async def fail(
        self,
        context: ExecutionContext,
        reason: str,
        allocation: Optional[Any] = None,
    ) -> None:

        await context.mark_failed(reason)

        if allocation is not None:

            try:

                await self.allocator.release(
                    allocation.allocation_id
                )

            except Exception:
                pass

        self.active_executions.pop(
            context.execution_id,
            None,
        )

        async with self._lock:

            self.metrics.failed_tasks += 1

            self.metrics.execution_failures += 1

            self.metrics.active_tasks = max(
                0,
                self.metrics.active_tasks - 1,
            )

        if (
            context.metadata.retry_count
            < self.DEFAULT_MAX_RETRIES
        ):

            await context.mark_retry()

            self.metrics.retry_count += 1

    # ========================================================
    # METRICS
    # ========================================================

    def _update_average_execution(
        self,
        duration_ms: float,
    ) -> None:

        completed = (
            self.metrics.completed_tasks
        )

        if completed <= 1:

            self.metrics.average_execution_time_ms = (
                duration_ms
            )

            return

        current = (
            self.metrics.average_execution_time_ms
        )

        self.metrics.average_execution_time_ms = (
            (
                current * (completed - 1)
            )
            + duration_ms
        ) / completed

    def get_metrics(
        self,
    ) -> FabricMetrics:

        return self.metrics

    # ========================================================
    # HEALTH
    # ========================================================

    async def health_check(
        self,
    ) -> Dict[str, Any]:

        queue_health = (
            await self.queue.health_check()
        )

        router_health = (
            await self.router.health_check()
        )

        allocator_health = (
            await self.allocator.health_check()
        )

        return {
            "status": self.status.value,
            "active_executions": len(
                self.active_executions
            ),
            "metrics": {
                "submitted": self.metrics.submitted_tasks,
                "completed": self.metrics.completed_tasks,
                "failed": self.metrics.failed_tasks,
                "active": self.metrics.active_tasks,
                "retries": self.metrics.retry_count,
            },
            "queue": queue_health,
            "router": router_health,
            "allocator": allocator_health,
        }
