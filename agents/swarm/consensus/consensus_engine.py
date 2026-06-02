"""
Institutional-Grade Swarm Consensus Engine
==========================================

Distributed Agentic Reasoning Framework (DARF)

Responsibilities:
- Distributed agreement
- Collective reasoning fusion
- Confidence aggregation
- Conflict resolution
- Consensus validation
- Hierarchical intelligence orchestration
"""

from __future__ import annotations

import asyncio
import statistics
import time
import uuid

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


# ============================================================
# CONSENSUS STRATEGIES
# ============================================================


class ConsensusStrategy(str, Enum):
    """
    Supported consensus strategies.
    """

    MAJORITY_VOTE = "majority_vote"

    WEIGHTED_CONFIDENCE = (
        "weighted_confidence"
    )

    UNANIMOUS = "unanimous"

    HIERARCHICAL = "hierarchical"

    HYBRID = "hybrid"


# ============================================================
# AGENT OPINION
# ============================================================


@dataclass(slots=True)
class AgentOpinion:
    """
    Swarm agent output.
    """

    agent_id: str

    response: str

    confidence_score: float

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# CONFLICT RECORD
# ============================================================


@dataclass(slots=True)
class ConflictRecord:
    """
    Conflict tracking structure.
    """

    conflict_id: str

    conflicting_agents: List[str]

    reason: str

    created_at: float = field(
        default_factory=time.time
    )


# ============================================================
# CONSENSUS RESULT
# ============================================================


@dataclass(slots=True)
class ConsensusResult:
    """
    Final consensus output.
    """

    consensus_id: str

    agreed_response: str

    participating_agents: List[str]

    confidence_score: float

    strategy_used: ConsensusStrategy

    conflicts_detected: List[
        ConflictRecord
    ]

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# CONSENSUS STATS
# ============================================================


@dataclass(slots=True)
class ConsensusStats:
    """
    Consensus engine metrics.
    """

    total_consensus_operations: int = 0

    successful_consensus: int = 0

    detected_conflicts: int = 0

    average_confidence: float = 0.0


# ============================================================
# CONSENSUS ENGINE
# ============================================================


class ConsensusEngine:
    """
    Institutional swarm consensus runtime.

    Features:
    - distributed agreement
    - weighted confidence aggregation
    - conflict detection
    - collective cognition fusion
    """

    def __init__(
        self,
    ) -> None:

        self._stats = (
            ConsensusStats()
        )

        self._lock = asyncio.Lock()

    # ========================================================
    # MAIN CONSENSUS
    # ========================================================

    async def build_consensus(
        self,
        opinions: List[AgentOpinion],
        strategy: ConsensusStrategy = (
            ConsensusStrategy.HYBRID
        ),
    ) -> ConsensusResult:
        """
        Build collective swarm consensus.
        """

        if not opinions:

            raise ValueError(
                "No opinions supplied."
            )

        conflicts = await self._detect_conflicts(
            opinions
        )

        if (
            strategy
            == ConsensusStrategy.MAJORITY_VOTE
        ):

            response = (
                await self._majority_vote(
                    opinions
                )
            )

        elif (
            strategy
            == ConsensusStrategy.WEIGHTED_CONFIDENCE
        ):

            response = (
                await self._weighted_consensus(
                    opinions
                )
            )

        elif (
            strategy
            == ConsensusStrategy.UNANIMOUS
        ):

            response = (
                await self._unanimous_consensus(
                    opinions
                )
            )

        else:

            response = (
                await self._hybrid_consensus(
                    opinions
                )
            )

        confidence = (
            await self._aggregate_confidence(
                opinions
            )
        )

        result = ConsensusResult(
            consensus_id=str(uuid.uuid4()),
            agreed_response=response,
            participating_agents=[
                opinion.agent_id
                for opinion in opinions
            ],
            confidence_score=confidence,
            strategy_used=strategy,
            conflicts_detected=conflicts,
            metadata={
                "opinion_count": len(
                    opinions
                ),
            },
        )

        async with self._lock:

            self._stats.total_consensus_operations += 1

            self._stats.successful_consensus += 1

            self._stats.detected_conflicts += len(
                conflicts
            )

            self._update_average_confidence(
                confidence
            )

        return result

    # ========================================================
    # MAJORITY VOTING
    # ========================================================

    async def _majority_vote(
        self,
        opinions: List[AgentOpinion],
    ) -> str:
        """
        Majority-based consensus.
        """

        counts: Dict[str, int] = {}

        for opinion in opinions:

            counts[
                opinion.response
            ] = counts.get(
                opinion.response,
                0,
            ) + 1

        return max(
            counts,
            key=counts.get,
        )

    # ========================================================
    # WEIGHTED CONFIDENCE
    # ========================================================

    async def _weighted_consensus(
        self,
        opinions: List[AgentOpinion],
    ) -> str:
        """
        Confidence-weighted consensus.
        """

        best = max(
            opinions,
            key=lambda opinion: (
                opinion.confidence_score
            ),
        )

        return best.response

    # ========================================================
    # UNANIMOUS CONSENSUS
    # ========================================================

    async def _unanimous_consensus(
        self,
        opinions: List[AgentOpinion],
    ) -> str:
        """
        Strict unanimous agreement.
        """

        responses = {
            opinion.response
            for opinion in opinions
        }

        if len(responses) != 1:

            raise ValueError(
                "Unanimous consensus failed."
            )

        return opinions[0].response

    # ========================================================
    # HYBRID CONSENSUS
    # ========================================================

    async def _hybrid_consensus(
        self,
        opinions: List[AgentOpinion],
    ) -> str:
        """
        Hybrid institutional consensus.
        """

        weighted = (
            await self._weighted_consensus(
                opinions
            )
        )

        majority = (
            await self._majority_vote(
                opinions
            )
        )

        if weighted == majority:
            return weighted

        return weighted

    # ========================================================
    # CONFLICT DETECTION
    # ========================================================

    async def _detect_conflicts(
        self,
        opinions: List[AgentOpinion],
    ) -> List[ConflictRecord]:
        """
        Detect conflicting outputs.
        """

        conflicts = []

        unique_responses = {
            opinion.response
            for opinion in opinions
        }

        if len(unique_responses) <= 1:

            return conflicts

        conflicts.append(
            ConflictRecord(
                conflict_id=str(
                    uuid.uuid4()
                ),
                conflicting_agents=[
                    opinion.agent_id
                    for opinion in opinions
                ],
                reason=(
                    "Response divergence detected."
                ),
            )
        )

        return conflicts

    # ========================================================
    # CONFIDENCE AGGREGATION
    # ========================================================

    async def _aggregate_confidence(
        self,
        opinions: List[AgentOpinion],
    ) -> float:
        """
        Aggregate swarm confidence.
        """

        scores = [
            opinion.confidence_score
            for opinion in opinions
        ]

        return float(
            statistics.mean(scores)
        )

    # ========================================================
    # METRICS
    # ========================================================

    def _update_average_confidence(
        self,
        confidence: float,
    ) -> None:
        """
        Update confidence metrics.
        """

        total = (
            self._stats.total_consensus_operations
        )

        if total <= 1:

            self._stats.average_confidence = (
                confidence
            )

            return

        current = (
            self._stats.average_confidence
        )

        self._stats.average_confidence = (
            (
                current
                * (total - 1)
            )
            + confidence
        ) / total

    # ========================================================
    # STATS
    # ========================================================

    def get_stats(
        self,
    ) -> ConsensusStats:
        """
        Retrieve engine metrics.
        """

        return self._stats

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    async def health_check(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime diagnostics.
        """

        return {
            "status": "healthy",
            "total_consensus_operations": (
                self._stats.total_consensus_operations
            ),
            "successful_consensus": (
                self._stats.successful_consensus
            ),
            "detected_conflicts": (
                self._stats.detected_conflicts
            ),
            "average_confidence": (
                self._stats.average_confidence
            ),
        }
