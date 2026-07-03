"""
Distributed Agentic Reasoning Framework (DARF)

Base Agent

Purpose
-------
Provides the canonical base implementation for all
DARF agents, enforcing execution contracts and lifecycle hooks.

Responsibilities
----------------
- Lifecycle management (before_run/after_run)
- Standardized execution wrapper (try/except)
- Result generation (AgentResult)
- Contract enforcement

Design Principles
-----------------
- Template Method Pattern
- Observer pattern hooks
- Production-ready error boundaries
- Thread-safe execution

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import time
import uuid
import logging
from dataclasses import dataclass, field
from typing import Any, Dict

from agents.agent import Agent
from agents.agent_context import AgentContext
from agents.agent_result import AgentResult

# Initialize logger for production observability
logger = logging.getLogger(__name__)

__all__ = ["BaseAgent"]

# ============================================================
# BASE AGENT
# ============================================================

@dataclass(slots=True)
class BaseAgent(Agent):
    """
    Canonical base class for DARF agents.
    Inherits from Agent (ABC) to ensure the 'run' contract is strictly upheld.
    """

    # Provide defaults to satisfy Python dataclass inheritance rules
    id: str = field(default_factory=lambda: f"AGENT-{uuid.uuid4().hex.upper()}")
    name: str = "Base Agent"
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    # ========================================================
    # IDENTIFICATION
    # ========================================================

    @property
    def agent_id(self) -> str:
        return self.id

    # ========================================================
    # LIFECYCLE HOOKS
    # ========================================================

    def before_run(self, context: AgentContext) -> None:
        """Hook executed before run()."""
        context.current_agent = self.agent_id
        logger.debug(f"Agent '{self.id}' starting execution.")

    def after_run(self, context: AgentContext, result: AgentResult) -> None:
        """Hook executed after run()."""
        if result.has_output():
            context.set_output(self.agent_id, result.output)
        
        log_level = logging.INFO if result.succeeded() else logging.ERROR
        logger.log(log_level, f"Agent '{self.id}' completed. Success={result.succeeded()}")

    # ========================================================
    # EXECUTION (TEMPLATE METHOD)
    # ========================================================

    def execute(self, context: AgentContext, **kwargs: Any) -> AgentResult:
        """
        Public execution wrapper.
        Enforces timing, error boundary, and lifecycle hooks.
        """
        self.before_run(context)
        start_time = time.perf_counter()

        try:
            # Delegate to the abstract 'run' implementation
            output = self.run(context, **kwargs)
            duration = time.perf_counter() - start_time
            
            result = AgentResult(
                agent_id=self.agent_id,
                success=True,
                output=output,
                execution_time=duration
            )

        except Exception as exc:
            duration = time.perf_counter() - start_time
            logger.exception(f"Unhandled error in agent '{self.id}'")
            
            result = AgentResult(
                agent_id=self.agent_id,
                success=False,
                error=str(exc),
                execution_time=duration
            )

        self.after_run(context, result)
        return result

    # ========================================================
    # ABSTRACT CONTRACT
    # ========================================================

    def run(self, context: AgentContext, **kwargs: Any) -> Any:
        """
        Concrete subclasses must implement this core logic.
        """
        raise NotImplementedError(f"Agent '{self.id}' must implement run().")

    # ========================================================
    # SERIALIZATION & REPRESENTATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "version": self.version,
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.agent_id})"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id='{self.agent_id}'>"