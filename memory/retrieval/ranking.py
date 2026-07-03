"""
Distributed Agentic Reasoning Framework (DARF)

Ranking

Purpose
-------
Ranks retrieved memory items.

Responsibilities
----------------
- Similarity ranking
- Score sorting
- Top-K selection
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

__all__ = [
    "Ranking",
]
# ============================================================
# RANKING
# ============================================================

@dataclass(slots=True)
class Ranking:

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
       # ========================================================
    # RANK
    # ========================================================

    def rank(

        self,

        results: Dict[
            str,
            float,
        ],

    ) -> List[
        Tuple[
            str,
            float,
        ]
    ]:

        return sorted(

            results.items(),

            key=lambda item: item[1],

            reverse=True,

        )
         # ========================================================
    # TOP K
    # ========================================================

    def top_k(

        self,

        results: Dict[
            str,
            float,
        ],

        k: int,

    ) -> List[
        Tuple[
            str,
            float,
        ]
    ]:

        return self.rank(

            results,

        )[:k]
        # ========================================================
    # BEST
    # ========================================================

    def best(

        self,

        results: Dict[
            str,
            float,
        ],

    ) -> Tuple[
        str,
        float,
    ] | None:

        ranked = self.rank(

            results,

        )

        if not ranked:

            return None

        return ranked[0]
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

        return "Ranking"

    def __repr__(

        self,

    ) -> str:

        return "<Ranking>"