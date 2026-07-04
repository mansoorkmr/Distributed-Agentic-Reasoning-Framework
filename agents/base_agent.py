"""
Distributed Agentic Reasoning Framework (DARF)

Base Agent

Purpose
-------
Provides the canonical base implementation for all
DARF agents, enforcing execution contracts and lifecycle hooks.

Responsibilities
----------------
- Lifecycle management
- Standardized execution wrapper
- Result generation
- Contract enforcement

Design Principles
-----------------
- Template Method Pattern
- Production-ready error boundaries
- Thread-safe execution

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import logging
import time
import uuid

from dataclasses import dataclass, field
from typing import Any, Dict

from agents.agent import Agent
from agents.agent_context import AgentContext
from agents.agent_result import AgentResult

logger = logging.getLogger(__name__)

__all__ = ["BaseAgent"]

# ============================================================
# BASE AGENT
# ============================================================

@dataclass(slots=True)
class BaseAgent(Agent):
    """
    Canonical base class for every DARF agent.
    """

    id: str = field(
        default_factory=lambda: f"AGENT-{uuid.uuid4().hex.upper()}"
    )

    name: str = "Base Agent"

    description: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)

    version: str = "1.0"

    @property
    def agent_id(self) -> str:
        return self.id

    def before_run(
        self,
        context: AgentContext,
    ) -> None:

        context.current_agent = self.agent_id

        logger.debug(
            "Agent '%s' starting execution.",
            self.agent_id,
        )

    def after_run(
        self,
        context: AgentContext,
        result: AgentResult,
    ) -> None:

        if result.output is not None:
            context.set_output(
                self.agent_id,
                result.output,
            )

        logger.info(
            "Agent '%s' completed. Success=%s",
            self.agent_id,
            result.success,
        )

    def execute(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> AgentResult:

        self.before_run(context)

        start = time.perf_counter()

        try:

            output = self.run(
                context,
                **kwargs,
            )

            result = AgentResult(
                agent_id=self.agent_id,
                success=True,
                output=output,
                execution_time=time.perf_counter() - start,
            )

        except Exception as exc:

            logger.exception(
                "Unhandled error in agent '%s'",
                self.agent_id,
            )

            result = AgentResult(
                agent_id=self.agent_id,
                success=False,
                error=str(exc),
                execution_time=time.perf_counter() - start,
            )

        self.after_run(
            context,
            result,
        )

        return result

    def run(
        self,
        context: AgentContext,
        **kwargs: Any,
    ) -> Any:
        raise NotImplementedError(
            f"{self.__class__.__name__}.run() must be implemented."
        )

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
        return (
            f"<{self.__class__.__name__} "
            f"id='{self.agent_id}'>"
        )