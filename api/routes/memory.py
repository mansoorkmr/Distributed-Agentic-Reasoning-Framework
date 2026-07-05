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
):
    
    memory_size = (
        len(context.variables)
        + len(context.outputs)
    )

    return MemoryResponse(
        success=True,
        message="Memory status retrieved successfully.",
        status="Active",
        vector_store="FAISS",
        embedding_model="all-MiniLM-L6-v2",
        top_k=5,
        memory_size=memory_size,
        metrics={
            "variables": context.variable_count(),
            "outputs": context.output_count(),
        },
        context=context.to_dict(),
    )