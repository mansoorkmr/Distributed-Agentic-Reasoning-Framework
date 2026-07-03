"""
Distributed Agentic Reasoning Framework (DARF)

Tool

Core executable tool definition.
"""

from __future__ import annotations

import json
import uuid

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional


def _tool_id() -> str:
    return f"TOOL-{uuid.uuid4().hex.upper()}"


@dataclass(slots=True)
class Tool:

    tool_id: str = field(default_factory=_tool_id)

    name: str = ""

    description: str = ""

    callable: Optional[Callable[..., Any]] = None

    enabled: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ---------------------------------------------------------
    # State
    # ---------------------------------------------------------

    def enable(self) -> None:

        self.enabled = True

    def disable(self) -> None:

        self.enabled = False

    def is_enabled(self) -> bool:

        return self.enabled

    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------

    def execute(
        self,
        *args,
        **kwargs,
    ) -> Any:

        if not self.enabled:

            raise RuntimeError(
                f"Tool '{self.name}' is disabled."
            )

        if self.callable is None:

            return None

        return self.callable(
            *args,
            **kwargs,
        )

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self):

        return {

            "tool_id": self.tool_id,

            "name": self.name,

            "description": self.description,

            "enabled": self.enabled,

            "callable":
                None
                if self.callable is None
                else self.callable.__name__,

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(self):

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

        )

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __str__(self):

        state = "enabled" if self.enabled else "disabled"

        return f"{self.name} ({state})"

    def __repr__(self):

        return (

            f"<Tool "

            f"name='{self.name}' "

            f"enabled={self.enabled}>"

        )