"""
Institutional-Grade Research Agent
==================================

Distributed Agentic Reasoning Framework (DARF)

Flagship Autonomous Agent

Capabilities:
- Multi-step reasoning
- Retrieval augmentation
- Tool execution
- Distributed coordination
- Long-term memory
- Context orchestration
- Autonomous planning
"""

from __future__ import annotations

import asyncio
import time
import uuid

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from agents.communication.message_bus.distributed_bus import (
    DistributedMessageBus,
)
from agents.communication.message_bus.distributed_bus import (
    MessageType,
)

from agents.knowledge.rag.rag_pipeline import (
    RAGPipeline,
)

from agents.memory.episodic.episodic_memory import (
    EpisodicMemory,
)

from agents.memory.semantic.semantic_memory import (
    SemanticMemory,
)

from agents.memory.working.working_memory import (
    WorkingMemory,
)

from agents.orchestration.orchestration_engine import (
    OrchestrationEngine,
)

from agents.reasoning.reasoning_engine import (
    ReasoningEngine,
)

from agents.tools.execution.tool_executor import (
    ToolExecutor,
)

from agents.tools.registry.tool_registry import (
    ToolRegistry,
)


# ============================================================
# AGENT STATE
# ============================================================


@dataclass(slots=True)
class ResearchAgentState:
    """
    Runtime agent state.
    """

    agent_id: str

    active_tasks: int = 0

    completed_tasks: int = 0

    failed_tasks: int = 0

    last_execution_time: Optional[
        float
    ] = None

    status: str = "idle"


# ============================================================
# RESEARCH TASK
# ============================================================


@dataclass(slots=True)
class ResearchTask:
    """
    Agent research task.
    """

    task_id: str

    query: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at: float = field(
        default_factory=time.time
    )


# ============================================================
# RESEARCH RESULT
# ============================================================


@dataclass(slots=True)
class ResearchResult:
    """
    Agent execution result.
    """

    task_id: str

    success: bool

    response: str

    retrieved_context: Optional[
        str
    ] = None

    reasoning_trace: Optional[
        List[str]
    ] = None

    execution_time: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# RESEARCH AGENT
# ============================================================


class ResearchAgent:
    """
    Institutional autonomous research agent.

    Integrated systems:
    - memory
    - retrieval
    - reasoning
    - orchestration
    - tools
    - communication
    """

    def __init__(
        self,
        agent_id: Optional[str],
        working_memory: WorkingMemory,
        episodic_memory: EpisodicMemory,
        semantic_memory: SemanticMemory,
        rag_pipeline: RAGPipeline,
        reasoning_engine: ReasoningEngine,
        orchestration_engine: OrchestrationEngine,
        tool_registry: ToolRegistry,
        tool_executor: ToolExecutor,
        message_bus: DistributedMessageBus,
    ) -> None:

        self.agent_id = (
            agent_id
            or str(uuid.uuid4())
        )

        self.working_memory = (
            working_memory
        )

        self.episodic_memory = (
            episodic_memory
        )

        self.semantic_memory = (
            semantic_memory
        )

        self.rag_pipeline = (
            rag_pipeline
        )

        self.reasoning_engine = (
            reasoning_engine
        )

        self.orchestration_engine = (
            orchestration_engine
        )

        self.tool_registry = (
            tool_registry
        )

        self.tool_executor = (
            tool_executor
        )

        self.message_bus = (
            message_bus
        )

        self.state = (
            ResearchAgentState(
                agent_id=self.agent_id
            )
        )

    # ========================================================
    # MAIN EXECUTION
    # ========================================================

    async def execute(
        self,
        query: str,
        query_embedding: List[float],
    ) -> ResearchResult:
        """
        Execute full autonomous workflow.
        """

        task = ResearchTask(
            task_id=str(uuid.uuid4()),
            query=query,
        )

        started_at = time.time()

        self.state.active_tasks += 1

        self.state.status = "executing"

        try:

            # =================================================
            # STORE WORKING MEMORY
            # =================================================

            await self._store_working_context(
                task
            )

            # =================================================
            # RETRIEVAL AUGMENTATION
            # =================================================

            rag_result = (
                await self.rag_pipeline.retrieve_context(
                    query=query,
                    query_embedding=query_embedding,
                    top_k=5,
                )
            )

            # =================================================
            # REASONING
            # =================================================

            reasoning_output = (
                await self.reasoning_engine.reason(
                    query=query,
                    context=(
                        rag_result.injected_context
                    ),
                )
            )

            # =================================================
            # ORCHESTRATION
            # =================================================

            execution_plan = (
                await self.orchestration_engine.orchestrate(
                    goal=query,
                    reasoning_output=(
                        reasoning_output
                    ),
                )
            )

            # =================================================
            # TOOL DISCOVERY
            # =================================================

            available_tools = (
                await self.tool_registry.discover_tools()
            )

            # =================================================
            # DISTRIBUTED EVENT
            # =================================================

            await self.message_bus.publish(
                topic="research.execution",
                sender_id=self.agent_id,
                payload={
                    "task_id": task.task_id,
                    "query": query,
                    "tools_available": len(
                        available_tools
                    ),
                },
                message_type=(
                    MessageType.EVENT
                ),
            )

            # =================================================
            # BUILD FINAL RESPONSE
            # =================================================

            final_response = (
                await self._build_response(
                    query=query,
                    rag_context=(
                        rag_result.injected_context
                    ),
                    reasoning_output=(
                        reasoning_output
                    ),
                    execution_plan=(
                        execution_plan
                    ),
                )
            )

            # =================================================
            # STORE EPISODIC MEMORY
            # =================================================

            await self._store_episode(
                task=task,
                result=final_response,
            )

            execution_time = (
                time.time() - started_at
            )

            self.state.completed_tasks += 1

            self.state.last_execution_time = (
                execution_time
            )

            self.state.status = "idle"

            return ResearchResult(
                task_id=task.task_id,
                success=True,
                response=final_response,
                retrieved_context=(
                    rag_result.injected_context
                ),
                reasoning_trace=[
                    str(reasoning_output)
                ],
                execution_time=execution_time,
                metadata={
                    "agent_id": self.agent_id,
                    "execution_plan": str(
                        execution_plan
                    ),
                },
            )

        except Exception as error:

            self.state.failed_tasks += 1

            self.state.status = "failed"

            return ResearchResult(
                task_id=task.task_id,
                success=False,
                response=str(error),
                execution_time=(
                    time.time() - started_at
                ),
            )

        finally:

            self.state.active_tasks -= 1

    # ========================================================
    # WORKING MEMORY
    # ========================================================

    async def _store_working_context(
        self,
        task: ResearchTask,
    ) -> None:
        """
        Store active cognition state.
        """

        await self.working_memory.store(
            key=task.task_id,
            value={
                "query": task.query,
                "created_at": task.created_at,
            },
        )

    # ========================================================
    # EPISODIC MEMORY
    # ========================================================

    async def _store_episode(
        self,
        task: ResearchTask,
        result: str,
    ) -> None:
        """
        Store execution episode.
        """

        await self.episodic_memory.store_episode(
            agent_id=self.agent_id,
            episode={
                "task_id": task.task_id,
                "query": task.query,
                "result": result,
            },
        )

    # ========================================================
    # RESPONSE GENERATION
    # ========================================================

    async def _build_response(
        self,
        query: str,
        rag_context: str,
        reasoning_output: Any,
        execution_plan: Any,
    ) -> str:
        """
        Build final institutional response.
        """

        response_parts = [
            "=== DARF RESEARCH RESPONSE ===",
            "",
            f"QUERY:",
            query,
            "",
            "=== RETRIEVED CONTEXT ===",
            rag_context,
            "",
            "=== REASONING OUTPUT ===",
            str(reasoning_output),
            "",
            "=== EXECUTION PLAN ===",
            str(execution_plan),
        ]

        return "\n".join(
            response_parts
        )

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    async def health_check(
        self,
    ) -> Dict[str, Any]:
        """
        Agent diagnostics.
        """

        return {
            "agent_id": self.agent_id,
            "status": self.state.status,
            "active_tasks": (
                self.state.active_tasks
            ),
            "completed_tasks": (
                self.state.completed_tasks
            ),
            "failed_tasks": (
                self.state.failed_tasks
            ),
        }
