"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Institutional Execution Exception Hierarchy

Purpose
-------
Defines the canonical exception hierarchy used by the
DARF Execution Fabric.

Every execution subsystem raises exceptions derived from
DARFExecutionError.

Responsibilities
----------------
- Execution validation
- Planning failures
- Scheduling failures
- Queue failures
- Dispatcher failures
- Worker failures
- Timeout handling
- Cancellation handling
- Retry failures
- Resource failures
- Execution engine failures

Design Principles
-----------------
- Hierarchical inheritance
- Machine-readable error codes
- Context preservation
- Retry awareness
- Distributed-system compatibility
- Future cloud execution support

Thread Safety
-------------
Stateless.
Thread-safe.

"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Dict
from typing import Optional
from enum import Enum
from enum import unique

__all__ = [
    "ErrorSeverity",
    "ExecutionErrorCode",
    "DARFExecutionError",
    "ExecutionValidationError",
    "ExecutionPlanningError",
    "ExecutionSchedulingError",
    "ExecutionDispatchError",
    "ExecutionQueueError",
    "ExecutionWorkerError",
    "ExecutionTimeoutError",
    "ExecutionCancelledError",
    "RetryLimitExceededError",
    "ResourceAllocationError",
    "AgentExecutionError",
    "DependencyResolutionError",
    "ExecutionStateError",
    "ExecutionPolicyError",
    "ExecutionEngineError",
]

# ============================================================
# ERROR SEVERITY
# ============================================================


@unique
class ErrorSeverity(str, Enum):
    """
    Canonical execution error severity.
    """

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ============================================================
# EXECUTION ERROR CODES
# ============================================================


@unique
class ExecutionErrorCode(str, Enum):
    """
    Canonical execution error codes.
    """

    EXECUTION_ERROR = "EXECUTION_ERROR"
    EXECUTION_VALIDATION_ERROR = "EXECUTION_VALIDATION_ERROR"
    EXECUTION_PLANNING_ERROR = "EXECUTION_PLANNING_ERROR"
    EXECUTION_SCHEDULING_ERROR = "EXECUTION_SCHEDULING_ERROR"
    EXECUTION_DISPATCH_ERROR = "EXECUTION_DISPATCH_ERROR"
    EXECUTION_QUEUE_ERROR = "EXECUTION_QUEUE_ERROR"
    EXECUTION_WORKER_ERROR = "EXECUTION_WORKER_ERROR"
    EXECUTION_TIMEOUT_ERROR = "EXECUTION_TIMEOUT_ERROR"
    EXECUTION_CANCELLED = "EXECUTION_CANCELLED"
    RETRY_LIMIT_EXCEEDED = "RETRY_LIMIT_EXCEEDED"
    RESOURCE_ALLOCATION_ERROR = "RESOURCE_ALLOCATION_ERROR"
    AGENT_EXECUTION_ERROR = "AGENT_EXECUTION_ERROR"
    DEPENDENCY_RESOLUTION_ERROR = "DEPENDENCY_RESOLUTION_ERROR"
    EXECUTION_STATE_ERROR = "EXECUTION_STATE_ERROR"
    EXECUTION_POLICY_ERROR = "EXECUTION_POLICY_ERROR"
    EXECUTION_ENGINE_ERROR = "EXECUTION_ENGINE_ERROR"


class DARFExecutionError(Exception):
    """
    Base class for all execution-related exceptions.

    Every execution exception in DARF must inherit
    from this class.
    """

    __slots__ = (
        "message",
        "error_code",
        "severity",
        "context",
        "cause",
        "timestamp",
        "error_id",
    )

    def __init__(
        self,
        message: str,
        *,
        error_code: ExecutionErrorCode = ExecutionErrorCode.EXECUTION_ERROR,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:

        super().__init__(message)

        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.context = context or {}
        self.cause = cause

        self.timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        
        self.error_id = f"EXEC-{uuid.uuid4().hex[:8].upper()}"

    def __str__(self) -> str:
        return f"[{self.error_code.value}] {self.message}"

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"error_id='{self.error_id}' "
            f"error_code='{self.error_code.value}'>"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_id": self.error_id,
            "timestamp": self.timestamp,
            "message": self.message,
            "error_code": self.error_code.value,
            "severity": self.severity.value,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_exception(
        cls,
        exc: Exception,
        *,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "DARFExecutionError":

        return cls(
            message=message or str(exc),
            context=context,
            cause=exc,
            **kwargs,
        )


# ============================================================
# VALIDATION
# ============================================================


class ExecutionValidationError(DARFExecutionError):
    """
    Raised when an execution request
    fails validation.
    """

    __slots__ = ()

    def __init__(
        self,
        message: str = "Execution request validation failed.",
        **kwargs,
    ) -> None:

        super().__init__(
            message=message,
            error_code=ExecutionErrorCode.EXECUTION_VALIDATION_ERROR,
            **kwargs,
        )


# ============================================================
# PLANNING
# ============================================================


class ExecutionPlanningError(DARFExecutionError):
    """
    Raised when execution planning
    cannot be completed.
    """

    __slots__ = ()

    def __init__(
        self,
        message: str = "Execution planning failed.",
        **kwargs,
    ) -> None:

        super().__init__(
            message=message,
            error_code=ExecutionErrorCode.EXECUTION_PLANNING_ERROR,
            **kwargs,
        )


# ============================================================
# SCHEDULING
# ============================================================


class ExecutionSchedulingError(DARFExecutionError):
    """
    Raised when task scheduling
    fails.
    """

    __slots__ = ()

    def __init__(
        self,
        message: str = "Execution scheduling failed.",
        **kwargs,
    ) -> None:

        super().__init__(
            message=message,
            error_code=ExecutionErrorCode.EXECUTION_SCHEDULING_ERROR,
            **kwargs,
        )


# ============================================================
# DISPATCHING
# ============================================================


class ExecutionDispatchError(DARFExecutionError):
    """
    Raised when an execution
    dispatch operation fails.
    """

    __slots__ = ()

    def __init__(
        self,
        message: str = "Execution dispatch failed.",
        **kwargs,
    ) -> None:

        super().__init__(
            message=message,
            error_code=ExecutionErrorCode.EXECUTION_DISPATCH_ERROR,
            **kwargs,
        )


# ============================================================
# QUEUE
# ============================================================


class ExecutionQueueError(DARFExecutionError):
    """
    Raised when an execution
    queue operation fails.
    """

    __slots__ = ()

    def __init__(
        self,
        message: str = "Execution queue operation failed.",
        **kwargs,
    ) -> None:

        super().__init__(
            message=message,
            error_code=ExecutionErrorCode.EXECUTION_QUEUE_ERROR,
            **kwargs,
        )


# ============================================================
# WORKER
# ============================================================


class ExecutionWorkerError(DARFExecutionError):
    """
    Raised when an execution
    worker encounters an error.
    """

    __slots__ = ()

    def __init__(
        self,
        message: str = "Execution worker encountered an error.",
        **kwargs,
    ) -> None:

        super().__init__(
            message=message,
            error_code=ExecutionErrorCode.EXECUTION_WORKER_ERROR,
            **kwargs,
        )


# ============================================================
# TIMEOUT
# ============================================================


class ExecutionTimeoutError(DARFExecutionError):
    """
    Raised when an execution
    times out.
    """

    __slots__ = ()

    def __init__(
        self,
        message: str = "Execution timed out.",
        **kwargs,
    ) -> None:

        super().__init__(
            message=message,
            error_code=ExecutionErrorCode.EXECUTION_TIMEOUT_ERROR,
            **kwargs,
        )


# ============================================================
# CANCELLED
# ============================================================


class ExecutionCancelledError(DARFExecutionError):
    """
    Raised when an execution
    is cancelled.
    """

    __slots__ = ()

    def __init__(
        self,
        message: str = "Execution was cancelled.",
        **kwargs,
    ) -> None:

        super().__init__(
            message=message,
            error_code=ExecutionErrorCode.EXECUTION_CANCELLED,
            **kwargs,
        )


# ============================================================
# RETRY
# ============================================================


class RetryLimitExceededError(DARFExecutionError):
    """
    Raised when execution retries
    exceed the maximum limit.
    """

    __slots__ = ()

    def __init__(
        self,
        message: str = "Execution retry limit exceeded.",
        **kwargs,
    ) -> None:

        super().__init__(
            message=message,
            error_code=ExecutionErrorCode.RETRY_LIMIT_EXCEEDED,
            **kwargs,
        )


# ============================================================
# RESOURCE
# ============================================================


class ResourceAllocationError(DARFExecutionError):
    """
    Raised when resource allocation
    fails during execution.
    """

    __slots__ = ()

    def __init__(
        self,
        message: str = "Resource allocation failed.",
        **kwargs,
    ) -> None:

        super().__init__(
            message=message,
            error_code=ExecutionErrorCode.RESOURCE_ALLOCATION_ERROR,
            **kwargs,
        )


# ============================================================
# AGENT
# ============================================================


class AgentExecutionError(DARFExecutionError):
    """
    Raised when a specific agent
    execution fails.
    """

    __slots__ = ()

    def __init__(
        self,
        message: str = "Agent execution failed.",
        **kwargs,
    ) -> None:

        super().__init__(
            message=message,
            error_code=ExecutionErrorCode.AGENT_EXECUTION_ERROR,
            **kwargs,
        )


# ============================================================
# DEPENDENCY
# ============================================================


class DependencyResolutionError(DARFExecutionError):
    """
    Raised when execution dependency
    resolution fails.
    """

    __slots__ = ()

    def __init__(
        self,
        message: str = "Dependency resolution failed.",
        **kwargs,
    ) -> None:

        super().__init__(
            message=message,
            error_code=ExecutionErrorCode.DEPENDENCY_RESOLUTION_ERROR,
            **kwargs,
        )


# ============================================================
# STATE
# ============================================================


class ExecutionStateError(DARFExecutionError):
    """
    Raised when an invalid execution
    state is encountered.
    """

    __slots__ = ()

    def __init__(
        self,
        message: str = "Invalid execution state encountered.",
        **kwargs,
    ) -> None:

        super().__init__(
            message=message,
            error_code=ExecutionErrorCode.EXECUTION_STATE_ERROR,
            **kwargs,
        )


# ============================================================
# POLICY
# ============================================================


class ExecutionPolicyError(DARFExecutionError):
    """
    Raised when an execution
    violates a defined policy.
    """

    __slots__ = ()

    def __init__(
        self,
        message: str = "Execution policy violation.",
        **kwargs,
    ) -> None:

        super().__init__(
            message=message,
            error_code=ExecutionErrorCode.EXECUTION_POLICY_ERROR,
            **kwargs,
        )


# ============================================================
# ENGINE
# ============================================================


class ExecutionEngineError(DARFExecutionError):
    """
    Raised for generic execution
    engine errors.
    """

    __slots__ = ()

    def __init__(
        self,
        message: str = "Execution engine error encountered.",
        **kwargs,
    ) -> None:

        super().__init__(
            message=message,
            error_code=ExecutionErrorCode.EXECUTION_ENGINE_ERROR,
            **kwargs,
        )