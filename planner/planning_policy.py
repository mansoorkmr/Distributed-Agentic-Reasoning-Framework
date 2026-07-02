"""
Distributed Agentic Reasoning Framework (DARF)
Planner

Planning Policy

Purpose
-------
Defines the canonical planning policy used by the
DARF Planner.

The planning policy controls how execution plans
are generated.

Responsibilities
----------------
- Planning configuration
- Dependency validation
- Parallelism control
- Optimization settings
- Serialization

Design Principles
-----------------
- Immutable configuration
- Strong typing
- Composition over inheritance
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

__all__ = [
    "PlanningPolicy",
]
# ============================================================
# PLANNING POLICY
# ============================================================


@dataclass(slots=True)
class PlanningPolicy:
    """
    Canonical planning policy.
    """

    max_depth: int = 32

    allow_parallelism: bool = True

    allow_dynamic_replanning: bool = False

    validate_dependencies: bool = True

    optimize_plan: bool = True

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

        if self.max_depth <= 0:

            raise ValueError(
                "max_depth must be > 0."
            )
            # ========================================================
    # HELPERS
    # ========================================================

    def is_parallelism_enabled(
        self,
    ) -> bool:

        return self.allow_parallelism

    def is_replanning_enabled(
        self,
    ) -> bool:

        return self.allow_dynamic_replanning

    def should_validate_dependencies(
        self,
    ) -> bool:

        return self.validate_dependencies

    def should_optimize_plan(
        self,
    ) -> bool:

        return self.optimize_plan
        # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[
        str,
        Any,
    ]:

        return {
            "max_depth": self.max_depth,
            "allow_parallelism": self.allow_parallelism,
            "allow_dynamic_replanning": (
                self.allow_dynamic_replanning
            ),
            "validate_dependencies": (
                self.validate_dependencies
            ),
            "optimize_plan": self.optimize_plan,
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(
        self,
    ) -> str:

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

        return (
            f"PlanningPolicy("
            f"depth={self.max_depth})"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<PlanningPolicy "
            f"depth={self.max_depth} "
            f"parallel={self.allow_parallelism}>"
        )