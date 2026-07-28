"""
Distributed Agentic Reasoning Framework (DARF)

Memory Route
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
)

from agents.agent_context import AgentContext

from api.dependencies import (
    get_agent_context,
    get_memory_agent,
)

from api.models.response import (
    MemoryResponse,
)

router = APIRouter(
    prefix="/memory",
    tags=["Memory"],
)


# ============================================================
# GET /memory
# ============================================================

@router.get(
    "",
    response_model=MemoryResponse,
)
def get_memory(
    context: AgentContext = Depends(
        get_agent_context,
    ),
    memory = Depends(
        get_memory_agent,
    ),
):
    
    memory_size = memory.memory.faiss_store.size()

    return MemoryResponse(
        success=True,
        message="Memory status retrieved successfully.",
        status="Active",
        vector_store="FAISS",
        embedding_model="all-MiniLM-L6-v2",
        top_k=5,
        memory_size=memory_size,
        metrics={
            "memory_size": memory.memory.faiss_store.size(),
            "top_k": memory.memory.top_k,
            "memory_health": memory.memory.health_check(),
            "working_memory": len(memory.memory.working.to_dict().get("keys", [])),
            "semantic_memory": memory.memory.semantic.count(),
            "episodic_memory": memory.memory.episodic.count(),
            "context_variables": context.variable_count(),
            "context_outputs": context.output_count(),
        },
        context=context.to_dict(),
    )