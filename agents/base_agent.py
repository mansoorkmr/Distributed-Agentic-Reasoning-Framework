from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Final
from dataclasses import dataclass


class AgentValidationError(Exception):
    """
    Raised when agent input validation fails.
    """
    pass


class AgentExecutionError(Exception):
    """
    Raised when agent execution fails.
    """
    pass


@dataclass(frozen=True)
class AgentContext:
    """
    Immutable execution context.

    Design:
        - Immutability prevents runtime mutation bugs
        - Strong typing ensures schema consistency

    Complexity:
        O(1) access for all fields
    """
    metadata: Dict[str, Any]
    user_id: Optional[str] = None


class BaseAgent(ABC):
    """
    Abstract Base Class for all agents.

    Design Patterns:
        - Template Method Pattern
        - Contract Enforcement Pattern

    Guarantees:
        ✔ Input validation enforced
        ✔ Execution contract fixed
        ✔ Errors are explicit and typed

    Complexity:
        execute(): O(1) wrapper + delegated implementation
    """

    name: Final[str]

    def __init__(self, name: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise AgentValidationError("Agent name must be a non-empty string")

        self.name = name.strip()

    def execute(self, task: str, context: AgentContext) -> str:
        """
        Public execution method (final contract).

        Steps:
            1. Validate inputs
            2. Execute implementation
            3. Validate output

        Complexity:
            O(1) wrapper
        """
        self._validate_input(task, context)

        try:
            result = self._execute_impl(task, context)
        except Exception as e:
            raise AgentExecutionError(
                f"Execution failed in agent '{self.name}': {str(e)}"
            ) from e

        self._validate_output(result)
        return result

    @abstractmethod
    def _execute_impl(self, task: str, context: AgentContext) -> str:
        """
        Core implementation (must be overridden).

        Complexity:
            Depends on subclass logic
        """
        raise NotImplementedError

    # =========================
    # VALIDATION LAYER
    # =========================

    def _validate_input(self, task: str, context: AgentContext) -> None:
        if not isinstance(task, str) or not task.strip():
            raise AgentValidationError("Task must be a non-empty string")

        if not isinstance(context, AgentContext):
            raise AgentValidationError("Invalid context type")

        if not isinstance(context.metadata, dict):
            raise AgentValidationError("Context metadata must be a dictionary")

    def _validate_output(self, result: str) -> None:
        if not isinstance(result, str):
            raise AgentExecutionError("Agent output must be a string")

        if not result.strip():
            raise AgentExecutionError("Agent returned empty output")
