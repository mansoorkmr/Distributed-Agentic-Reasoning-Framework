"""
Distributed Agentic Reasoning Framework (DARF)

Planner Registry
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any


@dataclass(slots=True)
class PlannerRegistry:

    planners: dict[str, Any] = field(
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
        name: str,
        planner: Any,
    ) -> None:

        self.planners[name] = planner

    def unregister(
        self,
        name: str,
    ) -> None:

        self.planners.pop(
            name,
            None,
        )

    def get(
        self,
        name: str,
    ) -> Any:

        return self.planners.get(name)

    def contains(
        self,
        name: str,
    ) -> bool:

        return name in self.planners

    def names(
        self,
    ) -> list[str]:

        return sorted(
            self.planners.keys()
        )

    def count(
        self,
    ) -> int:

        return len(
            self.planners
        )

    def is_empty(
        self,
    ) -> bool:

        return self.count() == 0

    def clear(
        self,
    ) -> None:

        self.planners.clear()

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self):

        return {

            "count":
                self.count(),

            "planners":
                self.names(),

            "metadata":
                self.metadata,

            "version":
                self.version,

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

        return (

            f"PlannerRegistry({self.count()} planners)"

        )

    def __repr__(self):

        return (

            f"<PlannerRegistry count={self.count()}>"

        )