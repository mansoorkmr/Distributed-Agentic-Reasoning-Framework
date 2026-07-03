"""
Distributed Agentic Reasoning Framework (DARF)

Runtime

Purpose
-------
Defines the canonical runtime for the DARF framework.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# Runtime Components
from runtime.runtime_context import RuntimeContext
from runtime.runtime_config import RuntimeConfig
from runtime.runtime_metrics import RuntimeMetrics
from runtime.runtime_registry import RuntimeRegistry

# Planning Components
from planner.planner import Planner
from planner.planner_result import PlannerResult

# Execution Components
from execution.execution_orchestrator import ExecutionOrchestrator

__all__ = ["Runtime"]

# ============================================================
# RUNTIME
# ============================================================

@dataclass(slots=True)
class Runtime:
    """
    Canonical DARF runtime.
    """

    config: RuntimeConfig = field(default_factory=RuntimeConfig)
    context: RuntimeContext = field(default_factory=RuntimeContext)
    metrics: RuntimeMetrics = field(default_factory=RuntimeMetrics)
    registry: RuntimeRegistry = field(default_factory=RuntimeRegistry)
    planner: Planner = field(default_factory=Planner)
    orchestrator: ExecutionOrchestrator = field(default_factory=ExecutionOrchestrator)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __post_init__(self) -> None:
        """Initialize the runtime."""
        self.metrics.reset()

    # ============================================================
    # STATUS
    # ============================================================

    def ready(self) -> bool:
        return True

    def planner_ready(self) -> bool:
        return self.planner is not None

    def orchestrator_ready(self) -> bool:
        return self.orchestrator is not None

    def registry_ready(self) -> bool:
        return self.registry is not None

    # ============================================================
    # AGENT REGISTRATION
    # ============================================================

    def register_agent(self, name: str, agent: Any) -> None:
        self.registry.register(name, agent)

    def unregister_agent(self, name: str) -> None:
        self.registry.unregister(name)

    def get_agent(self, name: str) -> Any:
        return self.registry.get(name)

    def has_agent(self, name: str) -> bool:
        return self.registry.contains(name)

    def agent_count(self) -> int:
        return self.registry.count()

    # ============================================================
    # EXECUTION
    # ============================================================

    def execute(self, objective: str) -> PlannerResult:
        """Execute a user objective."""
        if not objective:
            raise ValueError("objective cannot be empty.")

        # 1. Plan
        planner_result = self.planner.plan(objective)
        self.metrics.record_request()

        if not planner_result.success:
            self.metrics.record_failure()
            return planner_result

        # 2. Orchestrate
        self.orchestrator.load_plan(planner_result.execution_plan)
        
        agents = {name: self.registry.get(name) for name in self.registry.names()}
        self.orchestrator.execute(agents)

        self.metrics.record_success()
        return planner_result

    # ============================================================
    # METRICS & STATS
    # ============================================================

    def request_count(self) -> int:
        return self.metrics.requests

    def success_count(self) -> int:
        # Corrected: Mapping to existing RuntimeMetrics API
        return getattr(self.metrics, "success_count", 0)

    def failure_count(self) -> int:
        return self.metrics.failures

    def success_rate(self) -> float:
        # Corrected: Using the method defined in RuntimeMetrics
        if hasattr(self.metrics, "success_rate"):
            return self.metrics.success_rate()
        return 0.0

    # ============================================================
    # MAINTENANCE
    # ============================================================

    def reset(self) -> None:
        self.context.clear()
        self.metrics.reset()
        self.orchestrator.reset()
        self.metadata.clear()

    # ============================================================
    # SERIALIZATION
    # ============================================================

    def to_dict(self) -> Dict[str, Any]:
        return {
            "config": self.config.to_dict(),
            "context": self.context.to_dict(),
            "metrics": self.metrics.to_dict(),
            "registry": self.registry.to_dict(),
            "planner": self.planner.to_dict(),
            "orchestrator": self.orchestrator.to_dict(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ============================================================
    # REPRESENTATION
    # ============================================================

    def __str__(self) -> str:
        return f"Runtime({self.request_count()} requests)"

    def __repr__(self) -> str:
        return (
            f"<Runtime "
            f"requests={self.request_count()} "
            f"success={self.success_count()} "
            f"failed={self.failure_count()}>"
        )