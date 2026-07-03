"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Agent Executor

Purpose
-------
Executes registered agents on behalf of the
Execution Engine.

Responsibilities
----------------
- Locate agents
- Execute agents
- Capture results
- Update execution context
- Record metrics

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from execution.execution_context import ExecutionContext
from execution.execution_result import ExecutionResult

__all__ = [
    "AgentExecutor",
]

# ============================================================
# AGENT EXECUTOR
# ============================================================

@dataclass(slots=True)
class AgentExecutor:
    """
    Executes registered agents.
    """

    context: ExecutionContext = field(
        default_factory=ExecutionContext,
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict,
    )

    version: str = "1.0"

    # ============================================================
    # EXECUTION
    # ============================================================

    def execute(self, agent: Any, **kwargs: Any) -> ExecutionResult:
        """
        Execute an agent dynamically.
        """
        start = time.perf_counter()

        # Safely determine agent identity
        agent_id = getattr(agent, "agent_id", getattr(agent, "name", "unknown_agent"))
        self.context.current_agent = agent_id

        try:
            # Execute dynamically
            if hasattr(agent, "run"):
                output = agent.run(self.context, **kwargs)
            elif hasattr(agent, "execute"):
                output = agent.execute(self.context, **kwargs)
            else:
                raise AttributeError("Agent exposes neither 'run' nor 'execute'.")

            duration = time.perf_counter() - start

            # Update the shared execution context BEFORE returning
            self.context.set_output(agent_id, output)

            return ExecutionResult(
                success=True,
                output=output,
                duration=duration
            )

        except Exception as exc:
            duration = time.perf_counter() - start
            
            return ExecutionResult(
                success=False,
                error=str(exc),
                duration=duration
            )

    # ============================================================
    # STATISTICS & RESET
    # ============================================================

    def current_agent(self) -> Optional[str]:
        return self.context.current_agent

    def has_active_agent(self) -> bool:
        return self.context.current_agent is not None

    def reset(self) -> None:
        self.context.reset()
        self.metadata.clear()

    # ============================================================
    # SERIALIZATION & REPRESENTATION
    # ============================================================

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context": self.context.to_dict(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    def __str__(self) -> str:
        agent = self.context.current_agent or "None"
        return f"AgentExecutor(agent={agent})"

    def __repr__(self) -> str:
        return f"<AgentExecutor agent={self.context.current_agent!r}>"