"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Execution Queue

Purpose
-------
Defines the canonical execution queue used by the
DARF Execution Fabric.

The queue provides a thread-safe abstraction for
storing execution requests before they are processed
by execution workers.

Responsibilities
----------------
- FIFO execution queue
- Thread-safe enqueue/dequeue
- Queue inspection
- Capacity management
- Future distributed queue compatibility

Design Principles
-----------------
- Thread-safe
- Strong typing
- Backend agnostic
- Production ready

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

from queue import Empty
from queue import Full
from queue import Queue

from typing import Any
from typing import Optional


# ============================================================
# EXECUTION QUEUE
# ============================================================


@dataclass(slots=True)
class ExecutionQueue:
    """
    Canonical execution queue.
    """

    max_size: int = 0

    version: str = "1.0"

    _queue: Queue = field(
        init=False,
        repr=False,
    )

    def __post_init__(
        self,
    ) -> None:
        """
        Initialize the underlying queue.
        """

        if self.max_size < 0:
            raise ValueError(
                "max_size must be >= 0."
            )

        self._queue = Queue(
            maxsize=self.max_size
        )
            # ========================================================
    # QUEUE OPERATIONS
    # ========================================================

    def enqueue(
        self,
        item: Any,
        *,
        block: bool = True,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Insert an item into the queue.
        """

        self._queue.put(
            item,
            block=block,
            timeout=timeout,
        )

    def dequeue(
        self,
        *,
        block: bool = True,
        timeout: Optional[float] = None,
    ) -> Any:
        """
        Remove and return the next item.
        """

        return self._queue.get(
            block=block,
            timeout=timeout,
        )

    def peek(
        self,
    ) -> Optional[Any]:
        """
        Return the next queued item
        without removing it.

        Returns
        -------
        Optional[Any]
            The next queued item or None
            if the queue is empty.
        """

        with self._queue.mutex:
            if not self._queue.queue:
                return None

            return self._queue.queue[0]
            # ========================================================
    # QUEUE STATUS
    # ========================================================

    def size(
        self,
    ) -> int:
        """
        Return queue size.
        """

        return self._queue.qsize()

    def is_empty(
        self,
    ) -> bool:
        """
        Return True if queue is empty.
        """

        return self._queue.empty()

    def is_full(
        self,
    ) -> bool:
        """
        Return True if queue is full.
        """

        return self._queue.full()

    def clear(
        self,
    ) -> None:
        """
        Remove all queued items.
        """

        with self._queue.mutex:
            self._queue.queue.clear()
            self._queue.unfinished_tasks = 0
                # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize queue metadata.
        """

        return {
            "size": self.size(),
            "max_size": self.max_size,
            "is_empty": self.is_empty(),
            "is_full": self.is_full(),
            "version": self.version,
        }

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
            f"ExecutionQueue("
            f"{self.size()}/{self.max_size})"
        )

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"<ExecutionQueue "
            f"size={self.size()} "
            f"max_size={self.max_size}>"
        )
    