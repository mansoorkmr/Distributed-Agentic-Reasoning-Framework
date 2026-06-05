"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Runtime Metrics Infrastructure

Author:
    DARF Runtime Systems Division

Purpose:
    Enterprise-grade runtime metrics collection,
    aggregation, monitoring, observability,
    telemetry, and performance analytics.

Responsibilities:
    - execution telemetry
    - agent telemetry
    - runtime observability
    - latency analytics
    - throughput analytics
    - failure analytics
    - distributed monitoring
    - institutional reporting

Design Patterns:
    - Metrics Aggregator Pattern
    - Telemetry Collector Pattern
    - Snapshot Pattern
    - Immutable Export Pattern

Complexity:
    Metric update: O(1)
    Snapshot export: O(1)
    Metrics merge: O(n)
"""

from __future__ import annotations

import time

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from typing import Any
from typing import Dict
from typing import Optional


# ============================================================
# LATENCY AGGREGATOR
# ============================================================


@dataclass(slots=True)
class LatencyStatistics:
    """
    Incremental latency statistics.

    Complexity:
        O(1) updates
    """

    count: int = 0

    total_ms: float = 0.0

    minimum_ms: float = float("inf")

    maximum_ms: float = 0.0

    def record(
        self,
        latency_ms: float,
    ) -> None:

        if latency_ms < 0:
            raise ValueError(
                "Latency cannot be negative."
            )

        self.count += 1

        self.total_ms += latency_ms

        self.minimum_ms = min(
            self.minimum_ms,
            latency_ms,
        )

        self.maximum_ms = max(
            self.maximum_ms,
            latency_ms,
        )

    @property
    def average_ms(
        self,
    ) -> float:

        if self.count == 0:
            return 0.0

        return (
            self.total_ms
            /
            self.count
        )

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "count":
                self.count,
            "average_ms":
                self.average_ms,
            "minimum_ms":
                (
                    0.0
                    if self.count == 0
                    else self.minimum_ms
                ),
            "maximum_ms":
                self.maximum_ms,
            "total_ms":
                self.total_ms,
        }


# ============================================================
# THROUGHPUT STATS
# ============================================================


@dataclass(slots=True)
class ThroughputStatistics:
    """
    Runtime throughput analytics.

    Complexity:
        O(1)
    """

    started_at: float = field(
        default_factory=time.time
    )

    total_operations: int = 0

    def record_operation(
        self,
    ) -> None:

        self.total_operations += 1

    @property
    def operations_per_second(
        self,
    ) -> float:

        elapsed = (
            time.time()
            - self.started_at
        )

        if elapsed <= 0:
            return 0.0

        return (
            self.total_operations
            /
            elapsed
        )

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "total_operations":
                self.total_operations,
            "operations_per_second":
                self.operations_per_second,
        }


# ============================================================
# RUNTIME METRICS
# ============================================================


@dataclass(slots=True)
class RuntimeMetrics:
    """
    Institutional-grade runtime metrics.

    Tracks:
        - registrations
        - executions
        - failures
        - latency
        - throughput
        - health

    Complexity:
        O(1) updates
    """

    created_at: str = field(
        default_factory=lambda:
        datetime.utcnow().isoformat()
    )

    updated_at: str = field(
        default_factory=lambda:
        datetime.utcnow().isoformat()
    )

    # --------------------------------------------------------
    # AGENT METRICS
    # --------------------------------------------------------

    registered_agents: int = 0

    active_agents: int = 0

    disabled_agents: int = 0

    failed_agents: int = 0

    # --------------------------------------------------------
    # EXECUTION METRICS
    # --------------------------------------------------------

    executions_started: int = 0

    executions_completed: int = 0

    executions_failed: int = 0

    executions_cancelled: int = 0

    executions_timed_out: int = 0

    execution_retries: int = 0

    # --------------------------------------------------------
    # PERFORMANCE
    # --------------------------------------------------------

    latency: LatencyStatistics = field(
        default_factory=LatencyStatistics
    )

    throughput: ThroughputStatistics = field(
        default_factory=ThroughputStatistics
    )

    # --------------------------------------------------------
    # INTERNAL
    # --------------------------------------------------------

    last_execution_timestamp: Optional[
        str
    ] = None

    # ========================================================
    # UPDATE HELPERS
    # ========================================================

    def _touch(
        self,
    ) -> None:

        self.updated_at = (
            datetime.utcnow().isoformat()
        )

    # ========================================================
    # EXECUTION EVENTS
    # ========================================================

    def record_execution_started(
        self,
    ) -> None:

        self.executions_started += 1

        self.throughput.record_operation()

        self.last_execution_timestamp = (
            datetime.utcnow().isoformat()
        )

        self._touch()

    def record_execution_completed(
        self,
        latency_ms: float,
    ) -> None:

        self.executions_completed += 1

        self.latency.record(
            latency_ms
        )

        self.last_execution_timestamp = (
            datetime.utcnow().isoformat()
        )

        self._touch()

    def record_execution_failed(
        self,
    ) -> None:

        self.executions_failed += 1

        self.last_execution_timestamp = (
            datetime.utcnow().isoformat()
        )

        self._touch()

    def record_execution_timeout(
        self,
    ) -> None:

        self.executions_timed_out += 1

        self._touch()

    def record_execution_retry(
        self,
    ) -> None:

        self.execution_retries += 1

        self._touch()

    def record_execution_cancelled(
        self,
    ) -> None:

        self.executions_cancelled += 1

        self._touch()

    # ========================================================
    # AGENT EVENTS
    # ========================================================

    def update_registered_agents(
        self,
        count: int,
    ) -> None:

        if count < 0:

            raise ValueError(
                "Agent count cannot be negative."
            )

        self.registered_agents = count

        self._touch()

    def update_active_agents(
        self,
        count: int,
    ) -> None:

        if count < 0:

            raise ValueError(
                "Agent count cannot be negative."
            )

        self.active_agents = count

        self._touch()

    # ========================================================
    # DERIVED METRICS
    # ========================================================

    @property
    def success_rate(
        self,
    ) -> float:

        total = (
            self.executions_completed
            +
            self.executions_failed
        )

        if total == 0:
            return 0.0

        return (
            self.executions_completed
            /
            total
        ) * 100.0

    @property
    def failure_rate(
        self,
    ) -> float:

        total = (
            self.executions_completed
            +
            self.executions_failed
        )

        if total == 0:
            return 0.0

        return (
            self.executions_failed
            /
            total
        ) * 100.0

    # ========================================================
    # EXPORT
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "created_at":
                self.created_at,

            "updated_at":
                self.updated_at,

            "registered_agents":
                self.registered_agents,

            "active_agents":
                self.active_agents,

            "disabled_agents":
                self.disabled_agents,

            "failed_agents":
                self.failed_agents,

            "executions_started":
                self.executions_started,

            "executions_completed":
                self.executions_completed,

            "executions_failed":
                self.executions_failed,

            "executions_cancelled":
                self.executions_cancelled,

            "executions_timed_out":
                self.executions_timed_out,

            "execution_retries":
                self.execution_retries,

            "success_rate":
                self.success_rate,

            "failure_rate":
                self.failure_rate,
            "latency":
                self.latency.to_dict(),

            "throughput":
                self.throughput.to_dict(),

            "last_execution_timestamp":
                self.last_execution_timestamp,
        }

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
    ) -> None:

        fresh = RuntimeMetrics()

        self.created_at = fresh.created_at
        self.updated_at = fresh.updated_at

        self.registered_agents = (
            fresh.registered_agents
        )

        self.active_agents = (
            fresh.active_agents
        )

        self.disabled_agents = (
            fresh.disabled_agents
        )

        self.failed_agents = (
            fresh.failed_agents
        )

        self.executions_started = (
            fresh.executions_started
        )

        self.executions_completed = (
            fresh.executions_completed
        )

        self.executions_failed = (
            fresh.executions_failed
        )

        self.executions_cancelled = (
            fresh.executions_cancelled
        )

        self.executions_timed_out = (
            fresh.executions_timed_out
        )

        self.execution_retries = (
            fresh.execution_retries
        )

        self.latency = fresh.latency

        self.throughput = (
            fresh.throughput
        )

        self.last_execution_timestamp = (
            fresh.last_execution_timestamp
        )
