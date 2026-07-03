"""
Distributed Agentic Reasoning Framework (DARF)

Agent Result

Purpose
-------
Defines the canonical result returned by every DARF agent.

Responsibilities
----------------
- Store execution status, output, and error context
- Provide high-precision execution timing
- Handle robust serialization

Design Principles
-----------------
- Type-safe execution contracts
- Immutable-style state management
- Institutional-grade validation
- Production-ready
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

__all__ = ["AgentResult"]

# ============================================================
# AGENT RESULT
# ============================================================

@dataclass(slots=True)
class AgentResult:
    """
    Canonical result produced by an agent.
    """

    # Identity
    result_id: str = field(
        default_factory=lambda: f"AGENTRESULT-{uuid.uuid4().hex.upper()}"
    )
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
    version: str = "1.0"

    # Status
    success: bool = True
    output: Any = None
    error: Optional[str] = None
    
    # Timing
    execution_time: float = 0.0
    _start_time: float = field(
        default_factory=time.perf_counter, 
        init=False, 
        repr=False
    )

    # Context
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ========================================================
    # VALIDATION
    # ========================================================

    def __post_init__(self) -> None:
        """Validate result integrity."""
        if not self.result_id:
            raise ValueError("result_id cannot be empty.")
        if self.execution_time < 0:
            raise ValueError("execution_time must be >= 0.")
        if self.metadata is None:
            self.metadata = {}

    # ========================================================
    # STATE MANAGEMENT
    # ========================================================

    def finalize(self, success: bool, output: Any = None, error: Optional[str] = None) -> None:
        """
        Finalize the result state and calculate precise duration.
        Call this at the very end of an agent's run() method.
        """
        self.success = success
        self.output = output
        self.error = error
        self.execution_time = time.perf_counter() - self._start_time

    def succeeded(self) -> bool:
        return self.success

    def failed(self) -> bool:
        return not self.success

    def has_output(self) -> bool:
        return self.output is not None

    def has_error(self) -> bool:
        return self.error is not None

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialize result to dictionary."""
        return {
            "result_id": self.result_id,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": round(self.execution_time, 6),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        """Serialize result to JSON string."""
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"AgentResult({status}, {self.execution_time:.4f}s)"

    def __repr__(self) -> str:
        return f"<AgentResult id='{self.result_id}' agent='{self.agent_id}' success={self.success}>"