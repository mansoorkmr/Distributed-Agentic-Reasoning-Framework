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