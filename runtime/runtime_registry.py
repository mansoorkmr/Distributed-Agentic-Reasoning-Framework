"""
Distributed Agentic Reasoning Framework (DARF)

Runtime Registry
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict


@dataclass(slots=True)
class RuntimeRegistry:

    components: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register(
        self,
        name: str,
        component: Any,
    ) -> None:

        self.components[name] = component

    def unregister(
        self,
        name: str,
    ) -> None:

        self.components.pop(
            name,
            None,
        )

    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------

    def get(
        self,
        name: str,
        default: Any = None,
    ) -> Any:

        return self.components.get(
            name,
            default,
        )

    def contains(
        self,
        name: str,
    ) -> bool:

        return name in self.components

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------

    def clear(self) -> None:

        self.components.clear()

    def count(self) -> int:

        return len(
            self.components
        )

    def names(self):

        return sorted(
            self.components.keys()
        )

    def is_empty(self) -> bool:

        return self.count() == 0

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self):

        return {

            "count": self.count(),

            "components": self.names(),

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

        return (

            f"RuntimeRegistry({self.count()} components)"

        )

    def __repr__(self):

        return (

            "<RuntimeRegistry "

            f"count={self.count()}>"

        )