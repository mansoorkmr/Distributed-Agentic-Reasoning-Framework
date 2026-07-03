"""
Distributed Agentic Reasoning Framework (DARF)
Planner

Planner Exceptions

Purpose
-------
Defines the canonical exceptions raised by the
DARF Planner module.

Responsibilities
----------------
- Standardize error handling across the planner
- Differentiate distinct failure modes
- Provide clear debugging context

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

__all__ = [
    "PlannerError",
    "PlanningFailedError",
    "InvalidObjectiveError",
    "TaskDecompositionError",
    "DependencyResolutionError",
    "PlannerConfigurationError",
    "PlannerTimeoutError",
]

# ============================================================
# BASE EXCEPTION
# ============================================================

class PlannerError(Exception):
    """
    Base exception for all Planner-related errors.
    """
    pass


# ============================================================
# SPECIFIC EXCEPTIONS
# ============================================================

class PlanningFailedError(PlannerError):
    """
    Raised when the overall planning process fails
    to produce a valid execution plan.
    """
    pass


class InvalidObjectiveError(PlannerError):
    """
    Raised when the provided planning objective
    is null, malformed, or contextually invalid.
    """
    pass


class TaskDecompositionError(PlannerError):
    """
    Raised when the task decomposer fails to break
    down an objective into actionable tasks.
    """
    pass


class DependencyResolutionError(PlannerError):
    """
    Raised when the dependency graph contains cycles,
    missing links, or unresolvable dependencies.
    """
    pass


class PlannerConfigurationError(PlannerError):
    """
    Raised when the planner is initialized with
    invalid or conflicting configuration settings.
    """
    pass


class PlannerTimeoutError(PlannerError):
    """
    Raised when the planning sequence exceeds
    its allocated temporal constraints.
    """
    pass