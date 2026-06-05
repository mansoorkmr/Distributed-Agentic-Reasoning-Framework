"""
DARF Execution Context
======================

Distributed Agentic Reasoning Framework (DARF)

Responsibilities
---------------
- Distributed execution identity
- Task lineage tracking
- Distributed tracing
- Execution metadata
- Node assignment metadata
- Agent assignment metadata
- State transitions
- Serialization
- Recovery support
"""

from __future__ import annotations

import asyncio
import time
import uuid

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


# ============================================================
# EXECUTION MODE
# ============================================================


class ExecutionMode(str, Enum):
    """Execution deployment mode."""

    LOCAL = "local"

    DISTRIBUTED = "distributed"

    FEDERATED = "federated"

    HPC = "hpc"

    HYBRID = "hybrid"


# ============================================================
# EXECUTION STATUS
# ============================================================


class ExecutionStatus(str, Enum):
    """Execution lifecycle states."""

    PENDING = "pending"

    QUEUED = "queued"

    ROUTED = "routed"

    SCHEDULED = "scheduled"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    RETRYING = "retrying"

    CANCELLED = "cancelled"

    TIMEOUT = "timeout"


# ============================================================
# EXECUTION TRACE
# ============================================================


@dataclass(slots=True)
class ExecutionTrace:
    """
    Distributed execution lineage.
    """

    trace_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    root_trace_id: Optional[str] = None

    parent_trace_id: Optional[str] = None

    execution_path: List[str] = field(
        default_factory=list
    )

    created_at: float = field(
        default_factory=time.time
    )

    updated_at: float = field(
        default_factory=time.time
    )

    def add_step(self, step: str) -> None:
        """Append execution step."""

        self.execution_path.append(step)

        self.updated_at = time.time()


# ============================================================
# NODE CONTEXT
# ============================================================


@dataclass(slots=True)
class NodeContext:
    """
    Infrastructure execution node.
    """

    node_id: str

    hostname: str

    cluster: str = "default"

    region: str = "default"

    cpu_count: int = 0

    gpu_count: int = 0

    memory_gb: float = 0.0


# ============================================================
# EXECUTION METADATA
# ============================================================


@dataclass(slots=True)
class ExecutionMetadata:
    """
    Execution metadata container.
    """

    priority: int = 0

    retry_count: int = 0

    max_retries: int = 3

    timeout_seconds: int = 300

    tags: List[str] = field(
        default_factory=list
    )

    custom: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# EXECUTION RESULT CONTEXT
# ============================================================


@dataclass(slots=True)
class ExecutionResultContext:
    """
    Final execution information.
    """

    success: bool = False

    started_at: Optional[float] = None

    completed_at: Optional[float] = None

    latency_ms: Optional[float] = None

    error_message: Optional[str] = None

    output: Optional[Any] = None


# ============================================================
# EXECUTION CONTEXT
# ============================================================
class ExecutionContext:
    """
    Distributed execution context.

    Provides:
    - execution identity
    - tracing
    - state management
    - serialization
    - recovery metadata
    """

    VALID_TRANSITIONS = {
 
       # --------------------------------------------------------
       # INITIALIZATION
       # --------------------------------------------------------

    ExecutionStatus.PENDING: {
        ExecutionStatus.QUEUED,
        ExecutionStatus.CANCELLED,
    },

    # --------------------------------------------------------
    # QUEUEING
    # --------------------------------------------------------

    ExecutionStatus.QUEUED: {
        ExecutionStatus.ROUTED,
        ExecutionStatus.CANCELLED,
        ExecutionStatus.TIMEOUT,
    },

    # --------------------------------------------------------
    # ROUTING
    # --------------------------------------------------------

    ExecutionStatus.ROUTED: {
        ExecutionStatus.SCHEDULED,
        ExecutionStatus.CANCELLED,
        ExecutionStatus.TIMEOUT,
    },

    # --------------------------------------------------------
    # RESOURCE ALLOCATION
    # --------------------------------------------------------

    ExecutionStatus.SCHEDULED: {
        ExecutionStatus.RUNNING,
        ExecutionStatus.CANCELLED,
        ExecutionStatus.TIMEOUT,
    },

    # --------------------------------------------------------
    # EXECUTION
    # --------------------------------------------------------

    ExecutionStatus.RUNNING: {
        ExecutionStatus.COMPLETED,
        ExecutionStatus.FAILED,
        ExecutionStatus.TIMEOUT,
        ExecutionStatus.CANCELLED,
    },

    # --------------------------------------------------------
    # FAILURE HANDLING
    # --------------------------------------------------------

    ExecutionStatus.FAILED: {
        ExecutionStatus.RETRYING,
        ExecutionStatus.CANCELLED,
    },

    ExecutionStatus.RETRYING: {
        ExecutionStatus.QUEUED,
        ExecutionStatus.CANCELLED,
    },

    # --------------------------------------------------------
    # TERMINAL STATES
    # --------------------------------------------------------

    ExecutionStatus.COMPLETED: set(),

    ExecutionStatus.CANCELLED: set(),

    ExecutionStatus.TIMEOUT: set(),
}
    def __init__(
        self,
        task_id: str,
        agent_id: str,
        mode: ExecutionMode = ExecutionMode.LOCAL,
        correlation_id: Optional[str] = None,
        node_context: Optional[NodeContext] = None,
        metadata: Optional[
            ExecutionMetadata
        ] = None,
    ) -> None:

        self.execution_id = str(
            uuid.uuid4()
        )

        self.correlation_id = (
            correlation_id
            or str(uuid.uuid4())
        )

        self.task_id = task_id

        self.agent_id = agent_id

        self.mode = mode

        self.status = (
            ExecutionStatus.PENDING
        )

        self.trace = ExecutionTrace()

        self.node_context = (
            node_context
        )

        self.metadata = (
            metadata
            or ExecutionMetadata()
        )

        self.result = (
            ExecutionResultContext()
        )

        self.created_at = time.time()

        self.updated_at = (
            self.created_at
        )

        self._lock = asyncio.Lock()

        self.validate()

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate(self) -> None:
        """
        Validate context integrity.
        """

        if not self.task_id:
            raise ValueError(
                "task_id is required"
            )

        if not self.agent_id:
            raise ValueError(
                "agent_id is required"
            )

        if not isinstance(
            self.mode,
            ExecutionMode,
        ):
            raise ValueError(
                "invalid execution mode"
            )

    # ========================================================
    # STATE TRANSITIONS
    # ========================================================

    async def _transition(
        self,
        new_status: ExecutionStatus,
    ) -> None:

        async with self._lock:

            current = self.status

            allowed = (
                self.VALID_TRANSITIONS.get(
                    current,
                    set(),
                )
            )

            if (
                current
                not in (
                    ExecutionStatus.COMPLETED,
                    ExecutionStatus.CANCELLED,
                    ExecutionStatus.TIMEOUT,
                )
                and new_status
                not in allowed
            ):
                raise RuntimeError(
                    f"Invalid transition "
                    f"{current.value} -> "
                    f"{new_status.value}"
                )

            self.status = new_status

            self.updated_at = (
                time.time()
            )

            self.trace.add_step(
                new_status.value
            )

    async def mark_queued(self):
        await self._transition(
            ExecutionStatus.QUEUED
        )

    async def mark_routed(self):
        await self._transition(
            ExecutionStatus.ROUTED
        )

    async def mark_scheduled(self):
        await self._transition(
            ExecutionStatus.SCHEDULED
        )

    async def mark_running(self):
        self.result.started_at = (
            time.time()
        )

        await self._transition(
            ExecutionStatus.RUNNING
        )

    async def mark_completed(
        self,
        output: Any = None,
    ):
        self.result.success = True

        self.result.output = output

        self.result.completed_at = (
            time.time()
        )

        if self.result.started_at:

            self.result.latency_ms = (
                (
                    self.result.completed_at
                    - self.result.started_at
                )
                * 1000
            )

        await self._transition(
            ExecutionStatus.COMPLETED
        )

    async def mark_failed(
        self,
        error: str,
    ):
        self.result.success = False

        self.result.error_message = (
            error
        )

        await self._transition(
            ExecutionStatus.FAILED
        )

    async def mark_retry(self):
        self.metadata.retry_count += 1

        await self._transition(
            ExecutionStatus.RETRYING
        )

    async def mark_cancelled(self):
        await self._transition(
            ExecutionStatus.CANCELLED
        )

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary.
        """

        return {
            "execution_id": self.execution_id,
            "correlation_id": self.correlation_id,
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "mode": self.mode.value,
            "status": self.status.value,
            "trace": asdict(
                self.trace
            ),
            "node_context": (
                asdict(self.node_context)
                if self.node_context
                else None
            ),
            "metadata": asdict(
                self.metadata
            ),
            "result": asdict(
                self.result
            ),
            "created_at": (
                self.created_at
            ),
            "updated_at": (
                self.updated_at
            ),
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "ExecutionContext":
        """
        Reconstruct context from dictionary.
        """

        context = cls(
            task_id=data["task_id"],
            agent_id=data["agent_id"],
            mode=ExecutionMode(
                data["mode"]
            ),
            correlation_id=data[
                "correlation_id"
            ],
        )

        context.execution_id = data[
            "execution_id"
        ]

        context.status = (
            ExecutionStatus(
                data["status"]
            )
        )

        return context

    # ========================================================
    # INFO
    # ========================================================

    def is_terminal(self) -> bool:
        """
        Check terminal state.
        """

        return self.status in {
            ExecutionStatus.COMPLETED,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
            ExecutionStatus.TIMEOUT,
        }

    def age_seconds(self) -> float:
        """
        Execution age.
        """

        return (
            time.time()
            - self.created_at
        )

    def __repr__(
        self,
    ) -> str:

        return (
            "ExecutionContext("
            f"execution_id={self.execution_id}, "
            f"task_id={self.task_id}, "
            f"status={self.status.value})"
        )
