"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Execution Context Infrastructure

Author:
    DARF Runtime Systems Division

Purpose:
    Enterprise-grade execution context orchestration
    infrastructure for:

        - distributed agentic AI systems
        - institutional transformer runtimes
        - multi-agent orchestration
        - HPC-aware execution
        - inference scheduling
        - memory-aware reasoning
        - runtime reproducibility
        - scalable execution pipelines

Core Responsibilities:
    - runtime execution context management
    - distributed-safe request orchestration
    - generation parameter isolation
    - agent execution metadata
    - inference reproducibility
    - institutional observability
    - runtime telemetry
    - context lifecycle management

Design Principles:
    - immutable-safe
    - distributed-safe
    - production-grade
    - institutionally reproducible
    - telemetry-aware
    - extensible
    - deterministic
    - fault-tolerant

Supported Features:
    - request metadata tracking
    - generation configuration isolation
    - distributed execution metadata
    - latency instrumentation
    - runtime state tracking
    - execution lineage
    - HPC-aware orchestration
    - observability integration
"""

import json
import traceback
import uuid
from copy import deepcopy
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from infrastructure.logging.structured_logger import (
    get_logger,
)


@dataclass
class ExecutionContext:
    """
    Institutional-grade execution context.

    Represents:
        - runtime request metadata
        - generation configuration
        - distributed execution state
        - observability metadata
        - execution lineage
    """

    # ============================================================
    # CORE REQUEST METADATA
    # ============================================================

    request_id: str = field(
        default_factory=lambda: str(
            uuid.uuid4()
        )
    )

    session_id: Optional[str] = None

    user_query: str = ""

    timestamp_utc: str = field(
        default_factory=lambda: (
            datetime.utcnow().isoformat()
        )
    )

    # ============================================================
    # AGENT EXECUTION METADATA
    # ============================================================

    agent_name: Optional[str] = None

    execution_stage: str = (
        "initialized"
    )

    execution_priority: int = 1

    # ============================================================
    # GENERATION CONFIGURATION
    # ============================================================

    max_new_tokens: int = 512

    temperature: float = 0.7

    top_p: float = 0.95

    top_k: int = 50

    repetition_penalty: float = 1.1

    do_sample: bool = True

    use_cache: bool = True

    # ============================================================
    # RUNTIME CONFIGURATION
    # ============================================================

    device: str = "cuda"

    precision: str = "bf16"

    distributed: bool = False

    world_size: int = 1

    rank: int = 0

    # ============================================================
    # MEMORY & ATTENTION
    # ============================================================

    kv_cache_enabled: bool = True

    gradient_checkpointing: bool = False

    memory_optimized: bool = True

    # ============================================================
    # EXECUTION TELEMETRY
    # ============================================================

    start_time_utc: Optional[str] = None

    end_time_utc: Optional[str] = None

    latency_seconds: Optional[float] = None

    tokens_generated: int = 0

    # ============================================================
    # EXECUTION STATE
    # ============================================================

    success: bool = False

    error_message: Optional[str] = None

    warnings: List[str] = field(
        default_factory=list
    )

    # ============================================================
    # CUSTOM METADATA
    # ============================================================

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __post_init__(self):

        self.logger = get_logger(
            name="ExecutionContext",
            log_dir="logs/llm",
        )

        self._validate()

        self.logger.info(
            f"ExecutionContext initialized | "
            f"RequestID={self.request_id}"
        )

    # ============================================================
    # VALIDATION
    # ============================================================

    def _validate(self):
        """
        Validate execution context integrity.
        """

        if not isinstance(
            self.user_query,
            str,
        ):

            raise TypeError(
                "User query must be string."
            )

        if self.max_new_tokens <= 0:

            raise ValueError(
                "max_new_tokens must be > 0."
            )

        if not (
            0.0 <= self.temperature <= 5.0
        ):

            raise ValueError(
                "Temperature out of range."
            )

        if not (
            0.0 <= self.top_p <= 1.0
        ):

            raise ValueError(
                "top_p must be between 0 and 1."
            )

        if self.top_k < 0:

            raise ValueError(
                "top_k cannot be negative."
            )

        if self.world_size <= 0:

            raise ValueError(
                "world_size must be > 0."
            )

        if self.rank < 0:

            raise ValueError(
                "rank cannot be negative."
            )

        if self.rank >= self.world_size:

            raise ValueError(
                "Invalid distributed rank."
            )

    # ============================================================
    # EXECUTION LIFECYCLE
    # ============================================================

    def start_execution(self):
        """
        Mark execution start.
        """

        self.start_time_utc = (
            datetime.utcnow().isoformat()
        )

        self.execution_stage = (
            "running"
        )

        self.logger.info(
            f"Execution started | "
            f"RequestID={self.request_id}"
        )

    # ============================================================
    # COMPLETE EXECUTION
    # ============================================================

    def complete_execution(
        self,
        success: bool = True,
        tokens_generated: int = 0,
    ):
        """
        Mark execution completion safely.
        """

        self.end_time_utc = (
            datetime.utcnow().isoformat()
        )

        self.execution_stage = (
            "completed"
        )

        self.success = success

        self.tokens_generated = (
            tokens_generated
        )

        if self.start_time_utc:

            start = datetime.fromisoformat(
                self.start_time_utc
            )

            end = datetime.fromisoformat(
                self.end_time_utc
            )

            self.latency_seconds = (
                end - start
            ).total_seconds()

        self.logger.info(
            f"Execution completed | "
            f"RequestID={self.request_id} | "
            f"Latency={self.latency_seconds}"
        )

    # ============================================================
    # FAIL EXECUTION
    # ============================================================

    def fail_execution(
        self,
        error_message: str,
    ):
        """
        Mark execution failure safely.
        """

        self.end_time_utc = (
            datetime.utcnow().isoformat()
        )

        self.execution_stage = (
            "failed"
        )

        self.success = False

        self.error_message = (
            error_message
        )

        self.logger.error(
            f"Execution failed | "
            f"RequestID={self.request_id} | "
            f"Error={error_message}"
        )

    # ============================================================
    # WARNING MANAGEMENT
    # ============================================================

    def add_warning(
        self,
        warning: str,
    ):
        """
        Add runtime warning safely.
        """

        self.warnings.append(
            warning
        )

        self.logger.warning(
            f"Execution warning | "
            f"RequestID={self.request_id} | "
            f"Warning={warning}"
        )

    # ============================================================
    # CUSTOM METADATA
    # ============================================================

    def add_metadata(
        self,
        key: str,
        value: Any,
    ):
        """
        Add execution metadata safely.
        """

        self.metadata[key] = value

    # ============================================================
    # EXPORT AS DICTIONARY
    # ============================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Export execution context safely.
        """

        exported = asdict(self)

        exported.pop(
            "logger",
            None,
        )

        return deepcopy(exported)

    # ============================================================
    # EXPORT JSON
    # ============================================================

    def to_json(
        self,
        indent: int = 4,
    ) -> str:
        """
        Export execution context as JSON.
        """

        return json.dumps(

            self.to_dict(),

            indent=indent,

            ensure_ascii=False,
        )

    # ============================================================
    # SAFE EXECUTION WRAPPER
    # ============================================================

    def safe_update(
        self,
        updates: Dict[str, Any],
    ):
        """
        Fault-tolerant execution update.
        """

        try:

            for key, value in updates.items():

                if hasattr(self, key):

                    setattr(
                        self,
                        key,
                        value,
                    )

            self._validate()

        except Exception as error:

            self.logger.error(
                f"ExecutionContext update failed | "
                f"Error={error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

            raise error

    # ============================================================
    # SUMMARY
    # ============================================================

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return execution summary.
        """

        return {

            "request_id":
                self.request_id,

            "execution_stage":
                self.execution_stage,

            "success":
                self.success,

            "latency_seconds":
                self.latency_seconds,

            "tokens_generated":
                self.tokens_generated,

            "device":
                self.device,

            "distributed":
                self.distributed,

            "agent_name":
                self.agent_name,
        }

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return (
            f"ExecutionContext("
            f"request_id={self.request_id}, "
            f"stage={self.execution_stage}, "
            f"success={self.success})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    context = ExecutionContext(

        user_query=(
            "Explain distributed "
            "agentic reasoning systems."
        ),

        agent_name="planner_agent",

        distributed=True,

        world_size=4,

        rank=0,
    )

    context.start_execution()

    context.add_warning(
        "KV cache nearing threshold."
    )

    context.complete_execution(

        success=True,

        tokens_generated=512,
    )

    print("\nExecution Context Summary:\n")

    print(
        json.dumps(
            context.summary(),
            indent=4,
        )
    )
