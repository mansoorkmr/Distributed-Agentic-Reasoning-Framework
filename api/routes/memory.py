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

    return MemoryResponse(

        success=True,

        message="Current runtime context.",

        memory=context.to_dict(),

    )