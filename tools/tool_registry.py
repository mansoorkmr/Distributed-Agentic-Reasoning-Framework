"""
Distributed Agentic Reasoning Framework (DARF)

Tool Registry
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Dict
from typing import List
from typing import Optional

from tools.tool import Tool


@dataclass(slots=True)
class ToolRegistry:

    tools: Dict[str, Tool] = field(
        default_factory=dict
    )

    metadata: dict = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register(
        self,
        tool: Tool,
    ) -> None:

        self.tools[tool.tool_id] = tool

    def unregister(
        self,
        tool_id: str,
    ) -> None:

        self.tools.pop(
            tool_id,
            None,
        )

    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------

    def get(
        self,
        tool_id: str,
    ) -> Optional[Tool]:

        return self.tools.get(
            tool_id,
        )

    def find_by_name(
        self,
        name: str,
    ) -> Optional[Tool]:

        name = name.lower()

        for tool in self.tools.values():

            if tool.name.lower() == name:

                return tool

        return None

    def contains(
        self,
        tool_id: str,
    ) -> bool:

        return tool_id in self.tools

    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------

    def count(
        self,
    ) -> int:

        return len(
            self.tools
        )

    def is_empty(
        self,
    ) -> bool:

        return self.count() == 0

    def names(
        self,
    ) -> List[str]:

        return sorted(

            tool.name

            for tool in self.tools.values()

        )

    def all_tools(
        self,
    ) -> List[Tool]:

        return list(
            self.tools.values()
        )

    def clear(
        self,
    ) -> None:

        self.tools.clear()

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(
        self,
    ):

        return {

            "count": self.count(),

            "tools": [

                tool.to_dict()

                for tool in self.tools.values()

            ],

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(
        self,
    ):

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

        )

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __str__(
        self,
    ):

        return (

            f"ToolRegistry({self.count()} tools)"

        )

    def __repr__(
        self,
    ):

        return (

            "<ToolRegistry "

            f"count={self.count()}>"

        )