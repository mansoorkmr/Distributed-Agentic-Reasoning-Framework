"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Orchestration Engine Infrastructure

Author:
    DARF Orchestration Systems Division

Purpose:
    Enterprise-grade orchestration engine
    infrastructure for:

        - distributed multi-agent systems
        - institutional execution pipelines
        - scalable reasoning orchestration
        - HPC-aware workflow coordination
        - production-grade AI runtimes
        - distributed execution management
        - cognitive workflow orchestration
        - institutional AI infrastructure

Core Responsibilities:
    - orchestration lifecycle management
    - reasoning orchestration
    - decomposition orchestration
    - execution graph orchestration
    - coordination runtime orchestration
    - distributed-safe workflow execution
    - execution telemetry
    - institutional observability

Design Principles:
    - deterministic
    - distributed-safe
    - scalable
    - fault-tolerant
    - production-grade
    - institutionally reproducible
    - workflow-aware
    - future extensible

Supported Features:
    - end-to-end orchestration
    - reasoning pipelines
    - execution graph orchestration
    - distributed-safe coordination
    - execution lifecycle management
    - telemetry-aware orchestration
    - execution tracing
    - institutional workflow management
"""

import json
import traceback
import uuid
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional

from infrastructure.logging.structured_logger import (
    get_logger,
)

from agents.runtime.runtime_context import (
    RuntimeContext,
)

from agents.runtime.execution_state import (
    ExecutionState,
)

from agents.runtime.execution_state import (
    ExecutionStateManager,
)

from agents.reasoning.reasoning_engine import (
    ReasoningEngine,
)

from agents.reasoning.decomposition_engine import (
    DecompositionEngine,
)

from agents.coordination.execution_graph import (
    ExecutionGraph,
)

from agents.coordination.agent_coordinator import (
    AgentCoordinator,
)


class OrchestrationEngine:
    """
    Institutional-grade orchestration engine.

    Handles:
        - multi-agent orchestration
        - reasoning orchestration
        - execution graph orchestration
        - distributed-safe coordination
        - execution lifecycle management
    """

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(
        self,
        enable_reasoning: bool = True,
        enable_decomposition: bool = True,
        enable_execution_graph: bool = True,
        enable_coordination: bool = True,
        telemetry_enabled: bool = True,
    ):

        self.enable_reasoning = (
            enable_reasoning
        )

        self.enable_decomposition = (
            enable_decomposition
        )

        self.enable_execution_graph = (
            enable_execution_graph
        )

        self.enable_coordination = (
            enable_coordination
        )

        self.telemetry_enabled = (
            telemetry_enabled
        )

        self.logger = get_logger(

            name="OrchestrationEngine",

            log_dir="logs/agents",
        )

        # ========================================================
        # EXECUTION STATE
        # ========================================================

        self.state_manager = (
            ExecutionStateManager()
        )

        # ========================================================
        # SUBSYSTEMS
        # ========================================================

        self.reasoning_engine = (
            ReasoningEngine()
        )

        self.decomposition_engine = (
            DecompositionEngine()
        )

        self.execution_graph_engine = (
            ExecutionGraph()
        )

        self.agent_coordinator = (
            AgentCoordinator()
        )

        # ========================================================
        # TELEMETRY
        # ========================================================

        self.total_orchestrations = 0

        self.failed_orchestrations = 0

        self.created_at = (
            datetime.utcnow().isoformat()
        )

        self.logger.info(
            "OrchestrationEngine initialized successfully."
        )

    # ============================================================
    # VALIDATE QUERY
    # ============================================================

    def validate_query(
        self,
        query: str,
    ):
        """
        Validate orchestration query safely.
        """

        if query is None:

            raise ValueError(
                "Query cannot be None."
            )

        if not isinstance(
            query,
            str,
        ):

            raise TypeError(
                "Query must be string."
            )

        if len(
            query.strip()
        ) == 0:

            raise ValueError(
                "Query cannot be empty."
            )

    # ============================================================
    # BUILD ORCHESTRATION METADATA
    # ============================================================

    def build_orchestration_metadata(
        self,
        query: str,
    ) -> Dict[str, Any]:
        """
        Construct orchestration metadata safely.
        """

        return {

            "orchestration_id":
                str(uuid.uuid4()),

            "query":
                query,

            "timestamp":
                datetime.utcnow()
                .isoformat(),

            "orchestration_type":
                "distributed_agentic_execution",
        }

    # ============================================================
    # MAIN ORCHESTRATION PIPELINE
    # ============================================================

    def orchestrate(
        self,
        query: str,
        context: Optional[
            RuntimeContext
        ] = None,
    ) -> Dict[str, Any]:
        """
        Institutional-grade orchestration pipeline.
        """

        orchestration_start = (
            datetime.utcnow()
        )

        try:

            self.validate_query(query)

            self.total_orchestrations += 1

            # ----------------------------------------------------
            # CONTEXT INITIALIZATION
            # ----------------------------------------------------

            if context is None:

                context = RuntimeContext(

                    user_query=query
                )

            context.start_execution()

            orchestration_metadata = (
                self.build_orchestration_metadata(
                    query
                )
            )

            context.add_metadata(

                "orchestration_id",

                orchestration_metadata[
                    "orchestration_id"
                ],
            )

            # ----------------------------------------------------
            # STATE TRANSITIONS
            # ----------------------------------------------------

            self.state_manager.transition_to(

                ExecutionState.QUEUED
            )

            self.state_manager.transition_to(

                ExecutionState.PLANNING
            )

            # ----------------------------------------------------
            # REASONING ENGINE
            # ----------------------------------------------------

            reasoning_result = None

            if self.enable_reasoning:

                self.logger.info(
                    "Starting reasoning phase."
                )

                self.state_manager.transition_to(

                    ExecutionState.REASONING
                )

                reasoning_result = (

                    self.reasoning_engine
                    .reason(

                        query=query,

                        context=context,
                    )
                )

                if not reasoning_result.get(
                    "success",
                    False,
                ):

                    raise RuntimeError(
                        "Reasoning phase failed."
                    )

            # ----------------------------------------------------
            # DECOMPOSITION ENGINE
            # ----------------------------------------------------

            decomposition_result = None

            if self.enable_decomposition:

                self.logger.info(
                    "Starting decomposition phase."
                )

                decomposition_result = (

                    self.decomposition_engine
                    .decompose(

                        query=query,

                        context=context,
                    )
                )

                if not decomposition_result.get(
                    "success",
                    False,
                ):

                    raise RuntimeError(
                        "Decomposition phase failed."
                    )

            # ----------------------------------------------------
            # EXECUTION GRAPH
            # ----------------------------------------------------

            execution_graph_result = None

            if self.enable_execution_graph:

                self.logger.info(
                    "Building execution graph."
                )

                subtasks = (

                    decomposition_result[
                        "subtasks"
                    ]
                )

                execution_graph_result = (

                    self.execution_graph_engine
                    .build_graph(

                        subtasks=subtasks,

                        context=context,
                    )
                )

                if not execution_graph_result.get(
                    "success",
                    False,
                ):

                    raise RuntimeError(
                        "Execution graph phase failed."
                    )

            # ----------------------------------------------------
            # COORDINATION ENGINE
            # ----------------------------------------------------

            coordination_result = None

            if self.enable_coordination:

                self.logger.info(
                    "Starting coordination phase."
                )

                self.state_manager.transition_to(

                    ExecutionState.DISPATCHING
                )

                coordination_result = (

                    self.agent_coordinator
                    .coordinate(

                        execution_graph=
                        execution_graph_result,

                        context=context,
                    )
                )

                if not coordination_result.get(
                    "success",
                    False,
                ):

                    raise RuntimeError(
                        "Coordination phase failed."
                    )

            # ----------------------------------------------------
            # EXECUTION COMPLETION
            # ----------------------------------------------------

            self.state_manager.transition_to(

                ExecutionState.EXECUTING
            )

            self.state_manager.transition_to(

                ExecutionState.AGGREGATING
            )

            self.state_manager.transition_to(

                ExecutionState.COMPLETED
            )

            orchestration_end = (
                datetime.utcnow()
            )

            latency = (

                orchestration_end
                - orchestration_start
            ).total_seconds()

            context.complete_execution()

            result = {

                "orchestration_metadata":
                    orchestration_metadata,

                "reasoning":
                    reasoning_result,

                "decomposition":
                    decomposition_result,

                "execution_graph":
                    execution_graph_result,

                "coordination":
                    coordination_result,

                "runtime_context":
                    context.summary(),

                "execution_state":
                    self.state_manager
                    .summary(),

                "latency_seconds":
                    latency,

                "success":
                    True,

                "timestamp":
                    orchestration_end
                    .isoformat(),
            }

            self.logger.info(
                f"Orchestration completed | "
                f"RequestID="
                f"{context.request_id} | "
                f"Latency={latency:.4f}s"
            )

            return result

        except Exception as error:

            self.failed_orchestrations += 1

            try:

                self.state_manager.transition_to(

                    ExecutionState.FAILED
                )

            except Exception:

                pass

            if context is not None:

                context.fail_execution(
                    str(error)
                )

            self.logger.error(
                f"Orchestration failed | "
                f"Error={error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

            return {

                "success":
                    False,

                "error":
                    str(error),
            }

    # ============================================================
    # SAFE ORCHESTRATION
    # ============================================================

    def safe_orchestrate(
        self,
        query: str,
    ) -> Dict[str, Any]:
        """
        Fault-tolerant orchestration wrapper.
        """

        try:

            return self.orchestrate(
                query=query
            )

        except Exception as error:

            self.logger.error(
                f"Safe orchestration failed | "
                f"Error={error}"
            )

            return {

                "success":
                    False,

                "error":
                    str(error),
            }

    # ============================================================
    # TELEMETRY
    # ============================================================

    def telemetry(
        self,
    ) -> Dict[str, Any]:
        """
        Return institutional orchestration telemetry.
        """

        success_rate = 0.0

        if self.total_orchestrations > 0:

            success_rate = (

                (
                    self.total_orchestrations
                    - self.failed_orchestrations
                )

                / self.total_orchestrations
            )

        return {

            "total_orchestrations":
                self.total_orchestrations,

            "failed_orchestrations":
                self.failed_orchestrations,

            "success_rate":
                round(
                    success_rate,
                    4,
                ),

            "reasoning_enabled":
                self.enable_reasoning,

            "decomposition_enabled":
                self.enable_decomposition,

            "execution_graph_enabled":
                self.enable_execution_graph,

            "coordination_enabled":
                self.enable_coordination,

            "execution_state":
                self.state_manager
                .current_state
                .value,

            "created_at":
                self.created_at,
        }

    # ============================================================
    # EXPORT TELEMETRY
    # ============================================================

    def export_telemetry(
        self,
        output_path: str,
    ):
        """
        Export orchestration telemetry safely.
        """

        exported = {

            "orchestration_telemetry":
                self.telemetry(),

            "execution_state":
                self.state_manager
                .summary(),

            "reasoning_engine":
                self.reasoning_engine
                .telemetry(),

            "decomposition_engine":
                self.decomposition_engine
                .telemetry(),

            "execution_graph":
                self.execution_graph_engine
                .telemetry(),

            "agent_coordinator":
                self.agent_coordinator
                .telemetry(),
        }

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(

                exported,

                file,

                indent=4,

                ensure_ascii=False,
            )

        self.logger.info(
            f"Orchestration telemetry exported | "
            f"Path={output_path}"
        )

    # ============================================================
    # RESET ENGINE
    # ============================================================

    def reset(
        self,
    ):
        """
        Reset orchestration runtime safely.
        """

        self.state_manager.reset()

        self.execution_graph_engine.reset()

        self.logger.warning(
            "Orchestration engine reset."
        )

    # ============================================================
    # SUMMARY
    # ============================================================

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return institutional orchestration summary.
        """

        return {

            "reasoning_enabled":
                self.enable_reasoning,

            "decomposition_enabled":
                self.enable_decomposition,

            "execution_graph_enabled":
                self.enable_execution_graph,

            "coordination_enabled":
                self.enable_coordination,

            "telemetry_enabled":
                self.telemetry_enabled,

            "execution_state":
                self.state_manager
                .current_state
                .value,

            "created_at":
                self.created_at,
        }

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(
        self,
    ):

        return (

            f"OrchestrationEngine("
            f"orchestrations="
            f"{self.total_orchestrations}, "
            f"failed="
            f"{self.failed_orchestrations})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    orchestration_engine = (

        OrchestrationEngine(

            enable_reasoning=True,

            enable_decomposition=True,

            enable_execution_graph=True,

            enable_coordination=True,
        )
    )

    result = (

        orchestration_engine
        .orchestrate(

            query=(
                "Design a distributed "
                "institutional AI system "
                "for healthcare workflow "
                "automation."
            )
        )
    )

    print("\nOrchestration Result:\n")

    print(
        json.dumps(
            result,
            indent=4,
        )
    )

    print("\nOrchestration Telemetry:\n")

    print(
        json.dumps(
            orchestration_engine
            .telemetry(),
            indent=4,
        )
    )
