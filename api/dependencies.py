"""
Distributed Agentic Reasoning Framework (DARF)

FastAPI Dependency Providers
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from fastapi import HTTPException, status

from agents.agent_context import AgentContext
from agents.agent_manager import AgentManager
from bootstrap import get_application

if TYPE_CHECKING:
    from agents.llm_agent import LLMAgent

# Initialize application instance bound to dependencies
_application = get_application()

__all__ = [
    "get_agent_manager",
    "get_agent_context",
    "get_llm_agent",
    "reset_dependencies",
]


def get_agent_manager() -> AgentManager:
    """
    Return the shared AgentManager singleton.
    """
    return _application.get_manager()


def get_agent_context() -> AgentContext:
    """
    Return the shared AgentContext instance for processing scope.
    """
    return _application.get_context()


def get_llm_agent() -> LLMAgent:
    """
    Dependency injection target to retrieve the central LLMAgent 
    configured within the active framework manager container.
    """
    manager = get_agent_manager()
    
    # Safely extract the registered LLM agent using the correct manager schema
    agent = manager.get("llm")
    
    if agent is None:
        # Prevent 500 internal crashes if bootstrap failed or agent is missing
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The 'llm' agent is not currently registered in the AgentManager."
        )
        
    return agent  # type: ignore


def reset_dependencies() -> None:
    """
    Reset application dependencies.

    Primarily intended for testing environments.
    """
    global _application

    from bootstrap import initialize, reset

    reset()
    _application = initialize()