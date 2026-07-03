"""
Distributed Agentic Reasoning Framework (DARF)

Tool Context
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict
from typing import Optional


@dataclass(slots=True)
class ToolContext:

    request_id: Optional[str] = None

    execution_id: Optional[str] = None

    tool_id: Optional[str] = None

    caller_agent: Optional[str] = None

    arguments: Dict[str, Any] = field(
        default_factory=dict
    )

    variables: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ---------------------------------------------------------
    # Variables
    # ---------------------------------------------------------

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.variables[key] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.variables.get(
            key,
            default,
        )

    def remove(
        self,
        key: str,
    ) -> None:

        self.variables.pop(
            key,
            None,
        )

    def contains(
        self,
        key: str,
    ) -> bool:

        return key in self.variables

    def clear(self) -> None:

        self.variables.clear()

    def variable_count(self) -> int:

        return len(self.variables)

    def is_empty(self) -> bool:

        return self.variable_count() == 0

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self):

        return {

            "request_id": self.request_id,

            "execution_id": self.execution_id,

            "tool_id": self.tool_id,

            "caller_agent": self.caller_agent,

            "arguments": self.arguments,

            "variables": self.variables,

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(self):

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

            default=str,

        )

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __str__(self):

        return (

            f"ToolContext({self.variable_count()} variables)"

        )

    def __repr__(self):

        return (

            "<ToolContext "

            f"variables={self.variable_count()}>"

        )