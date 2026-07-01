"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Execution Policy

Purpose
-------
Defines the canonical execution policy used by the
DARF Execution Fabric.

The execution policy aggregates all execution-related
policies into a single configuration object.

Responsibilities
----------------
- Retry policy composition
- Timeout policy composition
- Execution configuration
- Validation
- Serialization

Design Principles
-----------------
- Composition over inheritance
- Strong typing
- Immutable policy configuration
- Production-ready serialization

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict

from execution.retry_policy import RetryPolicy
from execution.timeout_policy import TimeoutPolicy


# ============================================================
# EXECUTION POLICY
# ============================================================


@dataclass(
    slots=True,
)
class ExecutionPolicy:
    """
    Canonical execution policy for
    the DARF Execution Fabric.
    """

    retry: RetryPolicy = field(
        default_factory=RetryPolicy
    )

    timeout: TimeoutPolicy = field(
        default_factory=TimeoutPolicy
    )

    enable_metrics: bool = True

    enable_logging: bool = True

    enable_tracing: bool = False

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ========================================================
    # VALIDATION
    # ========================================================

    def __post_init__(
        self,
    ) -> None:
        """
        Validate execution policy.
        """

        if self.retry is None:
            raise ValueError(
                "retry policy cannot be None."
            )

        if self.timeout is None:
            raise ValueError(
                "timeout policy cannot be None."
            )
            # ========================================================
    # FEATURE FLAGS
    # ========================================================

    def is_metrics_enabled(
        self,
    ) -> bool:
        """
        Return True if execution metrics
        collection is enabled.
        """

        return self.enable_metrics

    def is_logging_enabled(
        self,
    ) -> bool:
        """
        Return True if execution logging
        is enabled.
        """

        return self.enable_logging

    def is_tracing_enabled(
        self,
    ) -> bool:
        """
        Return True if execution tracing
        is enabled.
        """

        return self.enable_tracing

    # ========================================================
    # POLICY ACCESSORS
    # ========================================================

    def get_retry_policy(
        self,
    ) -> RetryPolicy:
        """
        Return the configured retry policy.
        """

        return self.retry

    def get_timeout_policy(
        self,
    ) -> TimeoutPolicy:
        """
        Return the configured timeout policy.
        """

        return self.timeout

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Convert execution policy to a dictionary.
        """

        return {
            "retry": self.retry.to_dict(),
            "timeout": self.timeout.to_dict(),
            "enable_metrics": self.enable_metrics,
            "enable_logging": self.enable_logging,
            "enable_tracing": self.enable_tracing,
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(
        self,
    ) -> str:
        """
        Convert execution policy to JSON.
        """

        return json.dumps(
            self.to_dict(),
            indent=4,
            sort_keys=True,
        )

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
            "ExecutionPolicy("
            f"retry={self.retry.retry_strategy.value}, "
            f"timeout={self.timeout.timeout_seconds}s)"
        )

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"<ExecutionPolicy "
            f"retry='{self.retry.retry_strategy.value}' "
            f"timeout={self.timeout.timeout_seconds}s "
            f"metrics={self.enable_metrics} "
            f"logging={self.enable_logging} "
            f"tracing={self.enable_tracing}>"
        )