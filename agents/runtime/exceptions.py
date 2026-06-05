"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Runtime Exception Hierarchy

Author:
    DARF Runtime Systems Division

Purpose:
    Centralized exception infrastructure for:

        - Agent Runtime
        - Execution Fabric
        - Agent Registry
        - Agent Executor
        - Lifecycle Management
        - Distributed Orchestration
        - Recovery Systems
        - Runtime Monitoring

Design Goals:
    - Strong typing
    - Explicit failure domains
    - Distributed-safe diagnostics
    - Production-grade observability
    - Structured exception metadata
    - Deterministic error handling

Design Patterns:
    - Exception Hierarchy Pattern
    - Domain-Driven Error Modeling
    - Structured Diagnostics Pattern

Complexity:
    Exception creation: O(1)
    Metadata serialization: O(n)
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional


# ============================================================
# ERROR METADATA
# ============================================================


@dataclass(slots=True)
class ErrorMetadata:
    """
    Structured runtime error metadata.

    Provides:
        - auditability
        - observability
        - distributed tracing
        - forensic debugging

    Complexity:
        O(1)
    """

    error_code: str

    component: str

    timestamp: str = field(
        default_factory=lambda: (
            datetime.utcnow().isoformat()
        )
    )

    correlation_id: Optional[str] = None

    execution_id: Optional[str] = None

    node_id: Optional[str] = None

    details: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# BASE EXCEPTION
# ============================================================


class DARFRuntimeError(Exception):
    """
    Root runtime exception.

    All DARF runtime exceptions must inherit
    from this type.

    Complexity:
        O(1)
    """

    def __init__(
        self,
        message: str,
        *,
        metadata: Optional[
            ErrorMetadata
        ] = None,
    ) -> None:

        super().__init__(message)

        self.message = message

        self.metadata = (
            metadata
            or ErrorMetadata(
                error_code="RUNTIME_ERROR",
                component="runtime",
            )
        )

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "error_type":
                self.__class__.__name__,
            "message":
                self.message,
            "error_code":
                self.metadata.error_code,
            "component":
                self.metadata.component,
            "timestamp":
                self.metadata.timestamp,
            "correlation_id":
                self.metadata.correlation_id,
            "execution_id":
                self.metadata.execution_id,
            "node_id":
                self.metadata.node_id,
            "details":
                self.metadata.details,
        }

    def __str__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}"
            f"("
            f"{self.message}"
            f")"
        )


# ============================================================
# VALIDATION
# ============================================================


class RuntimeValidationError(
    DARFRuntimeError
):
    """
    Runtime validation failure.

    Examples:
        - invalid request
        - invalid schema
        - malformed payload
        - invalid state
    """


class ContractViolationError(
    DARFRuntimeError
):
    """
    Interface contract violation.

    Examples:
        - agent contract mismatch
        - invalid runtime integration
        - schema incompatibility
    """


# ============================================================
# REGISTRY
# ============================================================


class AgentRegistrationError(
    DARFRuntimeError
):
    """
    Agent registration failure.
    """


class AgentAlreadyRegisteredError(
    AgentRegistrationError
):
    """
    Duplicate registration attempt.
    """


class AgentNotFoundError(
    AgentRegistrationError
):
    """
    Agent lookup failure.
    """


# ============================================================
# EXECUTION
# ============================================================


class AgentExecutionError(
    DARFRuntimeError
):
    """
    Agent execution failure.
    """


class AgentExecutionTimeoutError(
    AgentExecutionError
):
    """
    Agent execution timeout.
    """


class AgentExecutionCancelledError(
    AgentExecutionError
):
    """
    Agent execution cancelled.
    """


class AgentExecutionRetryExhaustedError(
    AgentExecutionError
):
    """
    Retry policy exhausted.
    """


# ============================================================
# LIFECYCLE
# ============================================================


class LifecycleError(
    DARFRuntimeError
):
    """
    Lifecycle management failure.
    """


class InvalidLifecycleTransitionError(
    LifecycleError
):
    """
    Invalid lifecycle transition.
    """


class LifecycleStateCorruptionError(
    LifecycleError
):
    """
    Lifecycle consistency failure.
    """


# ============================================================
# EXECUTION STATE
# ============================================================


class ExecutionStateError(
    DARFRuntimeError
):
    """
    Execution state failure.
    """


class InvalidExecutionStateError(
    ExecutionStateError
):
    """
    Invalid execution state.
    """


class StateTransitionError(
    ExecutionStateError
):
    """
    Invalid execution transition.
    """


# ============================================================
# CONTEXT
# ============================================================


class RuntimeContextError(
    DARFRuntimeError
):
    """
    Runtime context failure.
    """


class ContextSerializationError(
    RuntimeContextError
):
    """
    Runtime context serialization failure.
    """


class ContextValidationError(
    RuntimeContextError
):
    """
    Runtime context validation failure.
    """


# ============================================================
# DISTRIBUTED SYSTEM
# ============================================================


class DistributedRuntimeError(
    DARFRuntimeError
):
    """
    Distributed runtime failure.
    """


class NodeUnavailableError(
    DistributedRuntimeError
):
    """
    Requested node unavailable.
    """


class ResourceAllocationError(
    DistributedRuntimeError
):
    """
    Resource allocation failure.
    """


class RoutingError(
    DistributedRuntimeError
):
    """
    Routing failure.
    """


class SynchronizationError(
    DistributedRuntimeError
):
    """
    Distributed synchronization failure.
    """


# ============================================================
# RECOVERY
# ============================================================


class RecoveryError(
    DARFRuntimeError
):
    """
    Recovery subsystem failure.
    """


class RecoveryExhaustedError(
    RecoveryError
):
    """
    Recovery attempts exhausted.
    """


# ============================================================
# HEALTH
# ============================================================


class RuntimeHealthError(
    DARFRuntimeError
):
    """
    Runtime health monitoring failure.
    """


class HealthCheckFailedError(
    RuntimeHealthError
):
    """
    Health check failure.
    """


# ============================================================
# SECURITY
# ============================================================


class SecurityViolationError(
    DARFRuntimeError
):
    """
    Security policy violation.
    """


class AuthorizationError(
    SecurityViolationError
):
    """
    Authorization failure.
    """


class AuthenticationError(
    SecurityViolationError
):
    """
    Authentication failure.
    """


# ============================================================
# SYSTEM
# ============================================================


class ConfigurationError(
    DARFRuntimeError
):
    """
    Runtime configuration failure.
    """


class DependencyError(
    DARFRuntimeError
):
    """
    Dependency initialization failure.
    """


class InternalRuntimeError(
    DARFRuntimeError
):
    """
    Unexpected runtime failure.
    """
