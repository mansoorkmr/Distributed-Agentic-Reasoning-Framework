"""
Distributed Agentic Reasoning Framework (DARF)

Memory Policy

Purpose
-------
Defines configurable policies governing memory behavior.

Responsibilities
----------------
- Capacity management
- Eviction strategy
- Persistence policy
- Expiration policy
- Vector indexing policy
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict

__all__ = [
    "MemoryPolicy",
]
# ============================================================
# MEMORY POLICY
# ============================================================

@dataclass(slots=True)
class MemoryPolicy:
    """
    Configuration for memory behavior.
    """

    max_items: int = 1000

    eviction_strategy: str = "lru"

    enable_persistence: bool = True

    enable_vector_index: bool = True

    ttl_seconds: int | None = None

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
       # ========================================================
    # HELPERS
    # ========================================================

    def persistence_enabled(
        self,
    ) -> bool:

        return self.enable_persistence

    def vector_index_enabled(
        self,
    ) -> bool:

        return self.enable_vector_index

    def expiration_enabled(
        self,
    ) -> bool:

        return self.ttl_seconds is not None

    def has_capacity(
        self,
        current_items: int,
    ) -> bool:

        return current_items < self.max_items
         # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[
        str,
        Any,
    ]:

        return {

            "max_items": self.max_items,

            "eviction_strategy": self.eviction_strategy,

            "enable_persistence": self.enable_persistence,

            "enable_vector_index": self.enable_vector_index,

            "ttl_seconds": self.ttl_seconds,

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(
        self,
    ) -> str:

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

        )
        # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(
        self,
    ) -> str:

        return (
            f"MemoryPolicy("
            f"capacity={self.max_items})"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<MemoryPolicy "
            f"capacity={self.max_items} "
            f"eviction='{self.eviction_strategy}'>"
        )