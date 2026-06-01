"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Runtime Context Infrastructure

Author:
    DARF Runtime Systems Division

Purpose:
    Enterprise-grade runtime context orchestration
    infrastructure for:

        - distributed multi-agent systems
        - institutional orchestration runtimes
        - scalable execution coordination
        - HPC-aware workflow management
        - agent lifecycle orchestration
        - reasoning execution pipelines
        - distributed execution tracing
        - production-grade state management

Core Responsibilities:
    - runtime context management
    - execution metadata orchestration
    - distributed-safe context propagation
    - execution tracing
    - runtime observability
    - workflow lineage tracking
    - execution lifecycle coordination
    - institutional telemetry

Design Principles:
    - deterministic
    - distributed-safe
    - immutable-safe
    - production-grade
    - institutionally reproducible
    - scalable
    - fault-tolerant
    - future extensible

Supported Features:
    - hierarchical runtime contexts
    - execution metadata tracking
    - agent coordination metadata
    - distributed-safe propagation
    - runtime lineage tracing
    - telemetry integration
    - context serialization
    - lifecycle-safe updates
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


# ================================================================
# RUNTIME CONTEXT
# ================================================================

@dataclass
class RuntimeContext:
    """
    Institutional-grade runtime context.

    Represents:
        - distributed execution context
        - workflow orchestration metadata
        - execution lineage
        - runtime telemetry
        - agent coordination state
    """

    # ============================================================
    # CORE IDENTIFIERS
    # ============================================================

    request_id: str = field(
        default_factory=lambda: str(
            uuid.uuid4()
        )
    )

    session_id: Optional[str] = None

    workflow_id: Optional[str] = None

    parent_context_id: Optional[str] = None

    # ============================================================
    # EXECUTION METADATA
    # ============================================================

    user_query: str = ""

    execution_state: str = (
        "initialized"
    )

    execution_priority: int = 1

    execution_depth: int = 0

    # ============================================================
    # AGENT COORDINATION
    # ============================================================

    active_agents: List[str] = field(
        default_factory=list
    )

    scheduled_agents: List[str] = field(
        default_factory=list
    )

    completed_agents: List[str] = field(
        default_factory=list
    )

    failed_agents: List[str] = field(
        default_factory=list
    )

    # ============================================================
    # TASK MANAGEMENT
    # ============================================================

    active_tasks: List[str] = field(
        default_factory=list
    )

    completed_tasks: List[str] = field(
        default_factory=list
    )

    failed_tasks: List[str] = field(
        default_factory=list
    )

    # ============================================================
    # DISTRIBUTED EXECUTION
    # ============================================================

    distributed: bool = False

    world_size: int = 1

    rank: int = 0

    node_id: Optional[str] = None

    # ============================================================
    # EXECUTION TELEMETRY
    # ============================================================

    created_at: str = field(
        default_factory=lambda: (
            datetime.utcnow().isoformat()
        )
    )

    updated_at: Optional[str] = None

    start_time_utc: Optional[str] = None

    end_time_utc: Optional[str] = None

    latency_seconds: Optional[float] = None

    # ============================================================
    # RUNTIME METADATA
    # ============================================================

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    reasoning_trace: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    # ============================================================
    # EXECUTION STATUS
    # ============================================================

    success: bool = False

    error_message: Optional[str] = None

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __post_init__(self):

        self.logger = get_logger(

            name="RuntimeContext",

            log_dir="logs/agents",
        )

        self.updated_at = (
            self.created_at
        )

        self._validate()

        self.logger.info(
            f"RuntimeContext initialized | "
            f"RequestID={self.request_id}"
        )

    # ============================================================
    # VALIDATION
    # ============================================================

    def _validate(
        self,
    ):
        """
        Validate runtime context integrity safely.
        """

        if not isinstance(
            self.user_query,
            str,
        ):

            raise TypeError(
                "user_query must be string."
            )

        if self.execution_priority < 0:

            raise ValueError(
                "execution_priority "
                "cannot be negative."
            )

        if self.execution_depth < 0:

            raise ValueError(
                "execution_depth "
                "cannot be negative."
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
    # UPDATE TIMESTAMP
    # ============================================================

    def _touch(
        self,
    ):
        """
        Update runtime modification timestamp.
        """

        self.updated_at = (
            datetime.utcnow().isoformat()
        )

    # ============================================================
    # START EXECUTION
    # ============================================================

    def start_execution(
        self,
    ):
        """
        Start execution lifecycle safely.
        """

        self.start_time_utc = (
            datetime.utcnow().isoformat()
        )

        self.execution_state = (
            "running"
        )

        self._touch()

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
    ):
        """
        Complete execution lifecycle safely.
        """

        self.end_time_utc = (
            datetime.utcnow().isoformat()
        )

        self.success = success

        self.execution_state = (
            "completed"
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

        self._touch()

        self.logger.info(
            f"Execution completed | "
            f"RequestID={self.request_id}"
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

        self.execution_state = (
            "failed"
        )

        self.success = False

        self.error_message = (
            error_message
        )

        self._touch()

        self.logger.error(
            f"Execution failed | "
            f"RequestID={self.request_id} | "
            f"Error={error_message}"
        )

    # ============================================================
    # AGENT MANAGEMENT
    # ============================================================

    def add_active_agent(
        self,
        agent_name: str,
    ):
        """
        Register active agent safely.
        """

        if agent_name not in self.active_agents:

            self.active_agents.append(
                agent_name
            )

            self._touch()

    def complete_agent(
        self,
        agent_name: str,
    ):
        """
        Mark agent completion safely.
        """

        if agent_name in self.active_agents:

            self.active_agents.remove(
                agent_name
            )

        if (
            agent_name
            not in self.completed_agents
        ):

            self.completed_agents.append(
                agent_name
            )

        self._touch()

    def fail_agent(
        self,
        agent_name: str,
    ):
        """
        Mark agent failure safely.
        """

        if agent_name in self.active_agents:

            self.active_agents.remove(
                agent_name
            )

        if (
            agent_name
            not in self.failed_agents
        ):

            self.failed_agents.append(
                agent_name
            )

        self._touch()

    # ============================================================
    # TASK MANAGEMENT
    # ============================================================

    def add_task(
        self,
        task_name: str,
    ):
        """
        Register task safely.
        """

        if task_name not in self.active_tasks:

            self.active_tasks.append(
                task_name
            )

        self._touch()

    def complete_task(
        self,
        task_name: str,
    ):
        """
        Complete task safely.
        """

        if task_name in self.active_tasks:

            self.active_tasks.remove(
                task_name
            )

        if (
            task_name
            not in self.completed_tasks
        ):

            self.completed_tasks.append(
                task_name
            )

        self._touch()

    def fail_task(
        self,
        task_name: str,
    ):
        """
        Mark task failure safely.
        """

        if task_name in self.active_tasks:

            self.active_tasks.remove(
                task_name
            )

        if (
            task_name
            not in self.failed_tasks
        ):

            self.failed_tasks.append(
                task_name
            )

        self._touch()

    # ============================================================
    # REASONING TRACE
    # ============================================================

    def add_reasoning_step(
        self,
        reasoning_step: str,
    ):
        """
        Append reasoning trace safely.
        """

        self.reasoning_trace.append(
            reasoning_step
        )

        self._touch()

    # ============================================================
    # WARNING MANAGEMENT
    # ============================================================

    def add_warning(
        self,
        warning: str,
    ):
        """
        Register runtime warning safely.
        """

        self.warnings.append(
            warning
        )

        self._touch()

        self.logger.warning(
            f"Runtime warning | "
            f"RequestID={self.request_id} | "
            f"Warning={warning}"
        )

    # ============================================================
    # METADATA MANAGEMENT
    # ============================================================

    def add_metadata(
        self,
        key: str,
        value: Any,
    ):
        """
        Register metadata safely.
        """

        self.metadata[key] = value

        self._touch()

    # ============================================================
    # EXPORT DICTIONARY
    # ============================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Export runtime context safely.
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
        Export runtime context JSON safely.
        """

        return json.dumps(

            self.to_dict(),

            indent=indent,

            ensure_ascii=False,
        )

    # ============================================================
    # SUMMARY
    # ============================================================

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return institutional runtime summary.
        """

        return {

            "request_id":
                self.request_id,

            "execution_state":
                self.execution_state,

            "active_agents":
                len(self.active_agents),

            "completed_agents":
                len(self.completed_agents),

            "failed_agents":
                len(self.failed_agents),

            "active_tasks":
                len(self.active_tasks),

            "completed_tasks":
                len(self.completed_tasks),

            "failed_tasks":
                len(self.failed_tasks),

            "distributed":
                self.distributed,

            "world_size":
                self.world_size,

            "rank":
                self.rank,

            "success":
                self.success,

            "latency_seconds":
                self.latency_seconds,
        }

    # ============================================================
    # SAFE UPDATE
    # ============================================================

    def safe_update(
        self,
        updates: Dict[str, Any],
    ):
        """
        Fault-tolerant runtime update wrapper.
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

            self._touch()

        except Exception as error:

            self.logger.error(
                f"RuntimeContext update failed | "
                f"Error={error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

            raise error

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(
        self,
    ):

        return (
            f"RuntimeContext("
            f"request_id={self.request_id}, "
            f"state={self.execution_state}, "
            f"success={self.success})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    context = RuntimeContext(

        user_query=(
            "Explain distributed "
            "multi-agent reasoning."
        ),

        distributed=True,

        world_size=4,

        rank=0,
    )

    context.start_execution()

    context.add_active_agent(
        "planner_agent"
    )

    context.add_task(
        "domain_analysis"
    )

    context.add_reasoning_step(
        "Analyzing domain requirements."
    )

    context.complete_task(
        "domain_analysis"
    )

    context.complete_agent(
        "planner_agent"
    )

    context.complete_execution()

    print("\nRuntime Context Summary:\n")

    print(
        json.dumps(
            context.summary(),
            indent=4,
        )
    )

    print("\nRuntime Context JSON:\n")

    print(
        context.to_json()
    )
