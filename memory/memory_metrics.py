"""
Distributed Agentic Reasoning Framework (DARF)

Memory Metrics

Purpose
-------
Collects runtime statistics for the memory subsystem.

Responsibilities
----------------
- Memory hits
- Memory misses
- Insertions
- Removals
- Hit ratio
- Miss ratio
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict

__all__ = [
    "MemoryMetrics",
]
# ============================================================
# MEMORY METRICS
# ============================================================

@dataclass(slots=True)
class MemoryMetrics:

    hits: int = 0

    misses: int = 0

    insertions: int = 0

    removals: int = 0

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
        # ========================================================
    # COUNTERS
    # ========================================================

    def record_hit(
        self,
    ) -> None:

        self.hits += 1

    def record_miss(
        self,
    ) -> None:

        self.misses += 1

    def record_insertion(
        self,
    ) -> None:

        self.insertions += 1

    def record_removal(
        self,
    ) -> None:

        self.removals += 1

    def reset(
        self,
    ) -> None:

        self.hits = 0
        self.misses = 0
        self.insertions = 0
        self.removals = 0
            # ========================================================
    # STATISTICS
    # ========================================================

    def total_queries(
        self,
    ) -> int:

        return self.hits + self.misses

    def hit_rate(
        self,
    ) -> float:

        total = self.total_queries()

        if total == 0:
            return 0.0

        return self.hits / total

    def miss_rate(
        self,
    ) -> float:

        total = self.total_queries()

        if total == 0:
            return 0.0

        return self.misses / total
        # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "hits": self.hits,

            "misses": self.misses,

            "insertions": self.insertions,

            "removals": self.removals,

            "total_queries": self.total_queries(),

            "hit_rate": self.hit_rate(),

            "miss_rate": self.miss_rate(),

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

            f"MemoryMetrics("

            f"hits={self.hits}, "

            f"misses={self.misses})"

        )

    def __repr__(
        self,
    ) -> str:

        return (

            f"<MemoryMetrics "

            f"queries={self.total_queries()}>"

        )