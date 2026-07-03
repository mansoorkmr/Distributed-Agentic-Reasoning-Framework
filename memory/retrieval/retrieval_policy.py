"""
Distributed Agentic Reasoning Framework (DARF)

Retrieval Policy

Purpose
-------
Defines configurable retrieval behavior for memory search.

Responsibilities
----------------
- Top-K retrieval
- Similarity threshold
- Exact vs semantic search
- Ranking strategy
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict

__all__ = [
    "RetrievalPolicy",
]
# ============================================================
# RETRIEVAL POLICY
# ============================================================

@dataclass(slots=True)
class RetrievalPolicy:
    """
    Retrieval configuration.
    """

    top_k: int = 5

    similarity_threshold: float = 0.75

    enable_exact_search: bool = True

    enable_semantic_search: bool = True

    ranking_strategy: str = "similarity"

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

    def exact_search_enabled(
        self,
    ) -> bool:

        return self.enable_exact_search

    def semantic_search_enabled(
        self,
    ) -> bool:

        return self.enable_semantic_search

    def valid_similarity(
        self,
        score: float,
    ) -> bool:

        return score >= self.similarity_threshold
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

            "top_k": self.top_k,

            "similarity_threshold":
                self.similarity_threshold,

            "enable_exact_search":
                self.enable_exact_search,

            "enable_semantic_search":
                self.enable_semantic_search,

            "ranking_strategy":
                self.ranking_strategy,

            "metadata":
                self.metadata,

            "version":
                self.version,

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
            f"RetrievalPolicy("
            f"top_k={self.top_k})"
        )

    def __repr__(
        self,
    ) -> str:

        return (

            "<RetrievalPolicy "

            f"top_k={self.top_k} "

            f"threshold={self.similarity_threshold}>"

        )