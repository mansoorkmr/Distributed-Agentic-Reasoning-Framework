"""
Distributed Agentic Reasoning Framework (DARF)

FastAPI Dependencies
"""

from __future__ import annotations

from agents.agent_context import AgentContext
from agents.agent_manager import AgentManager

__all__ = [
    "get_agent_manager",
    "get_agent_context",
    "reset_dependencies",
]


# ============================================================
# SINGLETON INSTANCES
# ============================================================

_manager = AgentManager()

_context = AgentContext()


# ============================================================
# DEPENDENCIES
# ============================================================

def get_agent_manager() -> AgentManager:
    """
    Return the shared AgentManager instance.
    """

    return _manager


def get_agent_context() -> AgentContext:
    """
    Return the shared AgentContext instance.
    """

    return _context


# ============================================================
# RESET
# ============================================================

def reset_dependencies() -> None:
    """
    Reset all shared runtime state.
    Useful during testing.
    """

    global _manager
    global _context

    _manager = AgentManager()

    _context = AgentContext()