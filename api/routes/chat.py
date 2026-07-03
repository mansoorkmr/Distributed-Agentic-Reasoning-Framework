"""
Distributed Agentic Reasoning Framework (DARF)

Chat Route
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from agents.llm_agent import LLMAgent
from agents.agent_context import AgentContext

from api.dependencies import (
    get_agent_context,
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
# SHARED AGENT
# ============================================================

_llm_agent = LLMAgent()

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

):

    result = _llm_agent.execute(

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