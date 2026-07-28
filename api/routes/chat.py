"""
Distributed Agentic Reasoning Framework (DARF)

Chat Route

Supports:
- Standard conversational chat
- Document-aware RAG chat
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from agents.agent_context import AgentContext

from api.dependencies import (
    get_agent_context,
    get_llm_agent,
)

from api.models.request import ChatRequest
from api.models.response import ChatResponse

from documents.document_store import document_store


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

    llm=Depends(
        get_llm_agent,
    ),
):
    """
    Execute a normal or document-aware DARF chat request.
    """

    llm_prompt = request.prompt
    retrieved_chunks: list[str] = []

    # ========================================================
    # DOCUMENT-AWARE RETRIEVAL
    # ========================================================

    if request.document_id:

        if not document_store.has_document(
            request.document_id
        ):
            raise HTTPException(
                status_code=404,
                detail=(
                    "The requested document is not available "
                    "in the active document store."
                ),
            )

        try:
            retrieved_chunks = document_store.search(
                document_id=request.document_id,
                query=request.prompt,
                top_k=5,
            )

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Document retrieval failed.",
            ) from exc

        if not retrieved_chunks:
            raise HTTPException(
                status_code=404,
                detail=(
                    "No relevant content could be retrieved "
                    "from the document."
                ),
            )

        document_context = "\n\n---\n\n".join(
            retrieved_chunks
        )

        llm_prompt = f"""
You are answering a question using an uploaded PDF document.

Use the DOCUMENT CONTEXT below as the primary source of information.

Do not invent information that is not supported by the document.

If the answer cannot be determined from the document context,
state that clearly.

DOCUMENT CONTEXT:
{document_context}

USER QUESTION:
{request.prompt}

ANSWER:
""".strip()

    # ========================================================
    # LLM EXECUTION
    # ========================================================

    result = llm.execute(
        context,
        prompt=llm_prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )

    if not result.success:

        raise HTTPException(
            status_code=500,
            detail=result.error
            or "LLM execution failed.",
        )

    # ========================================================
    # RESPONSE METADATA
    # ========================================================

    metadata = dict(
        result.metadata or {}
    )

    metadata["document_aware"] = bool(
        request.document_id
    )

    if request.document_id:
        metadata["document_id"] = request.document_id
        metadata["retrieved_chunks"] = len(
            retrieved_chunks
        )

    return ChatResponse(
        response=str(result.output),
        agent="llm",
        metadata=metadata,
    )