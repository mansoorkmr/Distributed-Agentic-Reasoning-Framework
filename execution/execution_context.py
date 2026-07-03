"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Execution Context

Purpose
-------
Shared execution context propagated through
the entire execution pipeline.

Responsibilities
----------------
- Request context
- Execution identifiers
- Runtime variables
- Shared outputs
- Agent state
- Tool state
- Memory state

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

__all__ = [
    "ExecutionContext",
]


# ============================================================
# EXECUTION CONTEXT
# ============================================================

@dataclass(slots=True)
class ExecutionContext:
    """
    Shared execution context.
    """

    request_id: Optional[str] = None
    execution_id: Optional[str] = None
    session_id: Optional[str] = None
    plan_id: Optional[str] = None

    current_task: Optional[str] = None
    current_agent: Optional[str] = None
    current_tool: Optional[str] = None

    variables: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    version: str = "1.0"

    # ============================================================
    # VARIABLES
    # ============================================================

    def set(self, name: str, value: Any) -> None:
        """
        Store a context variable.
        """
        self.variables[name] = value

    def get(self, name: str, default: Any = None) -> Any:
        """
        Retrieve a context variable.
        """
        return self.variables.get(name, default)

    def remove(self, name: str) -> bool:
        """
        Remove a context variable.
        """
        return self.variables.pop(name, None) is not None

    def contains(self, name: str) -> bool:
        """
        Determine whether a variable exists.
        """
        return name in self.variables

    def variable_count(self) -> int:
        """
        Return total variables.
        """
        return len(self.variables)

    # ============================================================
    # OUTPUTS
    # ============================================================

    def set_output(self, name: str, value: Any) -> None:
        """
        Store an execution output.
        """
        self.outputs[name] = value

    def output(self, name: str, default: Any = None) -> Any:
        """
        Retrieve an execution output.
        """
        return self.outputs.get(name, default)

    def has_output(self, name: str) -> bool:
        """
        Determine whether an output exists.
        """
        return name in self.outputs

    def remove_output(self, name: str) -> bool:
        """
        Remove an execution output.
        """
        return self.outputs.pop(name, None) is not None

    def output_count(self) -> int:
        """
        Return number of outputs.
        """
        return len(self.outputs)

    # ============================================================
    # CONTEXT STATE
    # ============================================================

    def clear(self) -> None:
        """
        Clear runtime variables,
        outputs and metadata.

        Execution identifiers are
        intentionally preserved.
        """
        self.variables.clear()
        self.outputs.clear()
        self.metadata.clear()

    def reset(self) -> None:
        """
        Reset the entire execution
        context.
        """
        self.request_id = None
        self.execution_id = None
        self.session_id = None
        self.plan_id = None

        self.current_task = None
        self.current_agent = None
        self.current_tool = None

        self.clear()

    def is_empty(self) -> bool:
        """
        Determine whether the context
        contains any runtime data.
        """
        return not self.variables and not self.outputs

    def has_request(self) -> bool:
        """
        Determine whether a request
        is active.
        """
        return self.request_id is not None

    def has_execution(self) -> bool:
        """
        Determine whether an execution
        is active.
        """
        return self.execution_id is not None

    def has_session(self) -> bool:
        """
        Determine whether a session
        exists.
        """
        return self.session_id is not None

    def has_plan(self) -> bool:
        """
        Determine whether a plan
        has been assigned.
        """
        return self.plan_id is not None

    # ============================================================
    # COLLECTION INTERFACE
    # ============================================================

    def __len__(self) -> int:
        """
        Return total stored items.
        """
        return self.variable_count() + self.output_count()

    def __contains__(self, key: str) -> bool:
        """
        Determine whether a variable
        or output exists.
        """
        return self.contains(key) or self.has_output(key)

    # ============================================================
    # SERIALIZATION
    # ============================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize execution context.
        """
        return {
            "request_id": self.request_id,
            "execution_id": self.execution_id,
            "session_id": self.session_id,
            "plan_id": self.plan_id,
            "current_task": self.current_task,
            "current_agent": self.current_agent,
            "current_tool": self.current_tool,
            "variables": self.variables,
            "outputs": self.outputs,
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        """
        Serialize execution context
        to JSON.
        """
        return json.dumps(
            self.to_dict(),
            indent=4,
            sort_keys=True,
        )

    # ============================================================
    # REPRESENTATION
    # ============================================================

    def __str__(self) -> str:
        """
        Human-readable representation.
        """
        return (
            f"ExecutionContext("
            f"{self.variable_count()} variables, "
            f"{self.output_count()} outputs)"
        )

    def __repr__(self) -> str:
        """
        Developer representation.
        """
        return (
            f"<ExecutionContext "
            f"request={self.request_id!r} "
            f"execution={self.execution_id!r} "
            f"variables={self.variable_count()} "
            f"outputs={self.output_count()}>"
        )