"""
Distributed Agentic Reasoning Framework (DARF)

Chat Route
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from agents.agent_context import AgentContext

from api.dependencies import (
    get_agent_context,
    get_llm_agent,
)

from api.models.request import (
    ChatRequest,
)

from api.models.response import (
    ChatResponse,
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

# ============================================================
# POST /chat
# ============================================================

@router.post(
    "",
    response_model=ChatResponse,
)
def chat(

    request: ChatRequest,

    context: AgentContext = Depends(
        get_agent_context,
    ),

    llm = Depends(
        get_llm_agent,
    ),

):

    result = llm.execute(

        context,

        prompt=request.prompt,

        temperature=request.temperature,

        max_tokens=request.max_tokens,

    )

    if not result.success:

        raise HTTPException(

            status_code=500,

            detail=result.error
            or "LLM execution failed.",

        )

    return ChatResponse(

        response=str(result.output),

        agent="llm",

        metadata=result.metadata,

    )