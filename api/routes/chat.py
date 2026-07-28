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
    get_memory_agent,
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

    memory = Depends(
        get_memory_agent,
    ),
):

    augmented_prompt = memory.memory.augment_prompt(
        request.prompt,
    )
    
    result = llm.execute(
        context,
        prompt=augmented_prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )

    if not result.success:
        raise HTTPException(
            status_code=500,
            detail=result.error or "LLM execution failed.",
        )

    # ============================================================
    # Persist conversation into long-term memory
    # ============================================================
    memory.memory.store(
        request.prompt,
        str(result.output),
    )

    return ChatResponse(
        response=str(result.output),
        agent="llm",
        metadata=result.metadata,
    )