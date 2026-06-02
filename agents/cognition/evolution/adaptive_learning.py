"""
Institutional-Grade Adaptive Learning Engine
============================================

Distributed Agentic Reasoning Framework (DARF)

Responsibilities:
- Self-improving cognition
- Adaptive optimization
- Reinforcement learning
- Recursive evolution
- Strategy adaptation
- Autonomous intelligence scaling
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
# LEARNING MODE
# ============================================================


class LearningMode(str, Enum):
    """
    Adaptive learning strategies.
    """

    REINFORCEMENT = "reinforcement"

    EVOLUTIONARY = "evolutionary"

    ADAPTIVE = "adaptive"

    RECURSIVE = "recursive"

    HYBRID = "hybrid"


# ============================================================
# LEARNING SIGNAL
# ============================================================


@dataclass(slots=True)
class LearningSignal:
    """
    Institutional learning signal.
    """

    signal_id: str

    source: str

    reward_score: float

    confidence_score: float

    execution_latency: float

    success: bool

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# EVOLUTION STRATEGY
# ============================================================


@dataclass(slots=True)
class EvolutionStrategy:
    """
    Cognitive optimization strategy.
    """

    strategy_id: str

    strategy_name: str

    adaptation_strength: float

    optimization_targets: List[
        str
    ]

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# LEARNING RESULT
# ============================================================


@dataclass(slots=True)
class LearningResult:
    """
    Final adaptive learning result.
    """

    learning_id: str

    signal: LearningSignal

    evolved_strategy: EvolutionStrategy

    improvement_score: float

    adaptive_adjustments: List[
        str
    ]

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# LEARNING METRICS
# ============================================================


@dataclass(slots=True)
class AdaptiveLearningMetrics:
    """
    Learning engine metrics.
    """

    total_learning_cycles: int = 0

    successful_optimizations: int = 0

    recursive_adaptations: int = 0

    average_improvement_score: float = 0.0


# ============================================================
# ADAPTIVE LEARNING ENGINE
# ============================================================


class AdaptiveLearningEngine:
    """
    Institutional continuous learning engine.

    Features:
    - recursive learning
    - adaptive cognition
    - reinforcement optimization
    - strategy evolution
    """

    def __init__(
        self,
    ) -> None:

        self._metrics = (
            AdaptiveLearningMetrics()
        )

        self._learning_history: List[
            LearningResult
        ] = []

        self._lock = asyncio.Lock()

    # ========================================================
    # MAIN LEARNING PIPELINE
    # ========================================================

    async def evolve(
        self,
        signal: LearningSignal,
        mode: LearningMode = (
            LearningMode.HYBRID
        ),
    ) -> LearningResult:
        """
        Execute institutional adaptive evolution.
        """

        evolved_strategy = (
            await self._generate_strategy(
                signal,
                mode,
            )
        )

        adaptive_adjustments = (
            await self._generate_adjustments(
                signal,
                evolved_strategy,
            )
        )

        improvement_score = (
            await self._calculate_improvement_score(
                signal,
                evolved_strategy,
            )
        )

        result = LearningResult(
            learning_id=str(
                uuid.uuid4()
            ),
            signal=signal,
            evolved_strategy=(
                evolved_strategy
            ),
            improvement_score=(
                improvement_score
            ),
            adaptive_adjustments=(
                adaptive_adjustments
            ),
            metadata={
                "mode": mode.value,
                "evolved_at": time.time(),
            },
        )

        async with self._lock:

            self._metrics.total_learning_cycles += 1

            self._metrics.successful_optimizations += 1

            self._metrics.recursive_adaptations += len(
                adaptive_adjustments
            )

            self._update_metrics(
                improvement_score
            )

            self._learning_history.append(
                result
            )

        return result

    # ========================================================
    # STRATEGY GENERATION
    # ========================================================

    async def _generate_strategy(
        self,
        signal: LearningSignal,
        mode: LearningMode,
    ) -> EvolutionStrategy:
        """
        Generate evolved optimization strategy.
        """

        optimization_targets = []

        adaptation_strength = 0.5

        if signal.success:

            optimization_targets.append(
                "Scale successful execution pathways."
            )

            adaptation_strength += 0.2

        else:

            optimization_targets.append(
                "Strengthen recovery mechanisms."
            )

        if signal.execution_latency > 3.0:

            optimization_targets.append(
                "Optimize execution latency."
            )

        if signal.confidence_score < 0.7:

            optimization_targets.append(
                "Increase reasoning validation."
            )

        return EvolutionStrategy(
            strategy_id=str(
                uuid.uuid4()
            ),
            strategy_name=(
                f"{mode.value}_optimization"
            ),
            adaptation_strength=round(
                min(adaptation_strength, 1.0),
                4,
            ),
            optimization_targets=(
                optimization_targets
            ),
            metadata={
                "mode": mode.value,
            },
        )

    # ========================================================
    # ADAPTIVE ADJUSTMENTS
    # ========================================================

    async def _generate_adjustments(
        self,
        signal: LearningSignal,
        strategy: EvolutionStrategy,
    ) -> List[str]:
        """
        Generate adaptive adjustments.
        """

        adjustments = []

        for target in (
            strategy.optimization_targets
        ):

            adjustments.append(
                f"Adaptive adjustment: {target}"
            )

        if not signal.success:

            adjustments.append(
                "Enable recursive fault tolerance."
            )

        if signal.reward_score < 0.5:

            adjustments.append(
                "Increase exploration depth."
            )

        return adjustments

    # ========================================================
    # IMPROVEMENT SCORING
    # ========================================================

    async def _calculate_improvement_score(
        self,
        signal: LearningSignal,
        strategy: EvolutionStrategy,
    ) -> float:
        """
        Compute adaptive improvement score.
        """

        base_score = (
            signal.reward_score
            * 0.5
        )

        confidence_bonus = (
            signal.confidence_score
            * 0.2
        )

        adaptation_bonus = (
            strategy.adaptation_strength
            * 0.3
        )

        return round(
            min(
                (
                    base_score
                    + confidence_bonus
                    + adaptation_bonus
                ),
                1.0,
            ),
            4,
        )

    # ========================================================
    # LEARNING HISTORY
    # ========================================================

    async def get_learning_history(
        self,
    ) -> List[LearningResult]:
        """
        Retrieve learning history.
        """

        async with self._lock:

            return list(
                self._learning_history
            )

    # ========================================================
    # METRICS
    # ========================================================

    def _update_metrics(
        self,
        score: float,
    ) -> None:
        """
        Update learning metrics.
        """

        total = (
            self._metrics.total_learning_cycles
        )

        if total <= 1:

            self._metrics.average_improvement_score = (
                score
            )

            return

        current = (
            self._metrics.average_improvement_score
        )

        self._metrics.average_improvement_score = (
            (
                current
                * (total - 1)
            )
            + score
        ) / total

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    async def health_check(
        self,
    ) -> Dict[str, Any]:
        """
        Institutional diagnostics.
        """

        return {
            "status": "healthy",
            "total_learning_cycles": (
                self._metrics.total_learning_cycles
            ),
            "successful_optimizations": (
                self._metrics.successful_optimizations
            ),
            "recursive_adaptations": (
                self._metrics.recursive_adaptations
            ),
            "average_improvement_score": (
                self._metrics.average_improvement_score
            ),
            "learning_history_size": len(
                self._learning_history
            ),
        }

    # ========================================================
    # METRICS ACCESS
    # ========================================================

    def get_metrics(
        self,
    ) -> AdaptiveLearningMetrics:
        """
        Retrieve adaptive learning metrics.
        """

        return self._metrics
