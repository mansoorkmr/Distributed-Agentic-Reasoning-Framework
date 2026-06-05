"""
DARF Execution Queue
===================

Institutional-grade distributed execution queue.

Responsibilities
----------------
- Priority scheduling
- Retry orchestration
- Delayed execution
- Dead letter handling
- Queue observability
- Backpressure management
"""

from __future__ import annotations

import asyncio
import heapq
import time
import uuid

from dataclasses import dataclass
from dataclasses import field
from enum import IntEnum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from infrastructure.distributed.fabric.execution_context import (
    ExecutionContext,
)


# ============================================================
# PRIORITY
# ============================================================


class QueuePriority(IntEnum):
    """
    Lower value = higher priority.
    """

    CRITICAL = 0

    HIGH = 1

    NORMAL = 2

    LOW = 3

    BACKGROUND = 4


# ============================================================
# QUEUE ITEM
# ============================================================


@dataclass(order=True)
class QueueItem:

    priority: int

    created_at: float

    item_id: str = field(compare=False)

    context: ExecutionContext = field(
        compare=False
    )

    payload: Dict[str, Any] = field(
        default_factory=dict,
        compare=False,
    )


# ============================================================
# DEAD LETTER
# ============================================================


@dataclass(slots=True)
class DeadLetterItem:

    item_id: str

    execution_id: str

    task_id: str

    failure_reason: str

    timestamp: float


# ============================================================
# METRICS
# ============================================================


@dataclass(slots=True)
class QueueMetrics:

    enqueued: int = 0

    dequeued: int = 0

    retries: int = 0

    dead_letters: int = 0

    delayed_tasks: int = 0

    current_depth: int = 0

    peak_depth: int = 0


# ============================================================
# EXECUTION QUEUE
# ============================================================


class ExecutionQueue:
    """
    Distributed execution queue.

    Supports:
    - priority scheduling
    - retry scheduling
    - delayed scheduling
    - dead letter processing
    """

    def __init__(
        self,
        max_queue_size: int = 10000,
    ) -> None:

        self._max_queue_size = (
            max_queue_size
        )

        self._priority_queue: List[
            QueueItem
        ] = []

        self._retry_queue: List[
            QueueItem
        ] = []

        self._delayed_queue: List[
            tuple[float, QueueItem]
        ] = []

        self._dead_letter_queue: List[
            DeadLetterItem
        ] = []

        self._metrics = QueueMetrics()

        self._lock = asyncio.Lock()

    # ========================================================
    # ENQUEUE
    # ========================================================

    async def enqueue(
        self,
        context: ExecutionContext,
        payload: Optional[
            Dict[str, Any]
        ] = None,
        priority: QueuePriority = (
            QueuePriority.NORMAL
        ),
    ) -> str:

        async with self._lock:

            if (
                len(self._priority_queue)
                >= self._max_queue_size
            ):
                raise RuntimeError(
                    "Execution queue full."
                )

            item = QueueItem(
                priority=int(priority),
                created_at=time.time(),
                item_id=str(
                    uuid.uuid4()
                ),
                context=context,
                payload=payload or {},
            )

            heapq.heappush(
                self._priority_queue,
                item,
            )

            self._metrics.enqueued += 1

            self._update_depth()

            return item.item_id

    # ========================================================
    # DEQUEUE
    # ========================================================

    async def dequeue(
        self,
    ) -> Optional[QueueItem]:

        async with self._lock:

            await self._promote_delayed()

            if not self._priority_queue:

                return None

            item = heapq.heappop(
                self._priority_queue
            )

            self._metrics.dequeued += 1

            self._update_depth()

            return item

    # ========================================================
    # RETRY
    # ========================================================

    async def retry(
        self,
        item: QueueItem,
    ) -> None:

        async with self._lock:

            heapq.heappush(
                self._retry_queue,
                item,
            )

            self._metrics.retries += 1

    # ========================================================
    # RETRY POP
    # ========================================================

    async def dequeue_retry(
        self,
    ) -> Optional[QueueItem]:

        async with self._lock:

            if not self._retry_queue:

                return None

            return heapq.heappop(
                self._retry_queue
            )

    # ========================================================
    # DELAYED TASKS
    # ========================================================

    async def schedule_delayed(
        self,
        item: QueueItem,
        delay_seconds: int,
    ) -> None:

        async with self._lock:

            execute_at = (
                time.time()
                + delay_seconds
            )

            heapq.heappush(
                self._delayed_queue,
                (
                    execute_at,
                    item,
                ),
            )

            self._metrics.delayed_tasks += 1

    async def _promote_delayed(
        self,
    ) -> None:

        now = time.time()

        while (
            self._delayed_queue
            and self._delayed_queue[0][0]
            <= now
        ):

            _, item = heapq.heappop(
                self._delayed_queue
            )

            heapq.heappush(
                self._priority_queue,
                item,
            )

    # ========================================================
    # DEAD LETTER
    # ========================================================

    async def push_dead_letter(
        self,
        context: ExecutionContext,
        reason: str,
    ) -> None:

        async with self._lock:

            self._dead_letter_queue.append(
                DeadLetterItem(
                    item_id=str(
                        uuid.uuid4()
                    ),
                    execution_id=(
                        context.execution_id
                    ),
                    task_id=context.task_id,
                    failure_reason=reason,
                    timestamp=time.time(),
                )
            )

            self._metrics.dead_letters += 1

    # ========================================================
    # INSPECTION
    # ========================================================

    async def queue_depth(
        self,
    ) -> Dict[str, int]:

        async with self._lock:

            return {
                "priority": len(
                    self._priority_queue
                ),
                "retry": len(
                    self._retry_queue
                ),
                "delayed": len(
                    self._delayed_queue
                ),
                "dead_letter": len(
                    self._dead_letter_queue
                ),
            }

    async def get_dead_letters(
        self,
    ) -> List[DeadLetterItem]:

        async with self._lock:

            return list(
                self._dead_letter_queue
            )

    # ========================================================
    # HEALTH
    # ========================================================

    async def health_check(
        self,
    ) -> Dict[str, Any]:

        depth = await self.queue_depth()

        return {
            "status": "healthy",
            "max_queue_size": (
                self._max_queue_size
            ),
            "queue_depth": depth,
            "metrics": {
                "enqueued": (
                    self._metrics.enqueued
                ),
                "dequeued": (
                    self._metrics.dequeued
                ),
                "retries": (
                    self._metrics.retries
                ),
                "dead_letters": (
                    self._metrics.dead_letters
                ),
            },
        }

    # ========================================================
    # METRICS
    # ========================================================

    def metrics(
        self,
    ) -> QueueMetrics:

        return self._metrics

    # ========================================================
    # DEPTH
    # ========================================================

    def _update_depth(
        self,
    ) -> None:

        depth = len(
            self._priority_queue
        )

        self._metrics.current_depth = (
            depth
        )

        if (
            depth
            > self._metrics.peak_depth
        ):

            self._metrics.peak_depth = (
                depth
            )
