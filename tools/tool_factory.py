"""
Distributed Agentic Reasoning Framework (DARF)

Tool Factory
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field
from typing import Callable
from typing import Optional

from tools.tool import Tool


@dataclass(slots=True)
class ToolFactory:

    metadata: dict = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ---------------------------------------------------------
    # Generic Tool
    # ---------------------------------------------------------

    def create(
        self,
        name: str,
        callable: Optional[Callable] = None,
        description: str = "",
    ) -> Tool:

        return Tool(
            name=name,
            description=description,
            callable=callable,
        )

    # ---------------------------------------------------------
    # Common Tool Types
    # ---------------------------------------------------------

    def create_python_tool(
        self,
        function: Callable,
        description: str = "",
    ) -> Tool:

        return Tool(
            name=function.__name__,
            description=description,
            callable=function,
        )

    def create_calculator_tool(
        self,
    ) -> Tool:

        def calculator(expression: str):

            return eval(
                expression,
                {"__builtins__": {}},
                {},
            )

        return Tool(
            name="Calculator",
            description="Evaluate arithmetic expression",
            callable=calculator,
        )

    def create_echo_tool(
        self,
    ) -> Tool:

        def echo(message):

            return message

        return Tool(
            name="Echo",
            description="Echo input",
            callable=echo,
        )

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self):

        return {

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

        return "ToolFactory"

    def __repr__(self):

        return "<ToolFactory>"