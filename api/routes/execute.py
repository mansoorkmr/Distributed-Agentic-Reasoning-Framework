"""
Distributed Agentic Reasoning Framework (DARF)

Execute Route
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from agents.agent_context import AgentContext
from agents.agent_manager import AgentManager

from api.dependencies import (
    get_agent_context,
    get_agent_manager,
)

from api.models.request import (
    ExecuteRequest,
)

from api.models.response import (
    ExecuteResponse,
)

router = APIRouter(

    prefix="/execute",

    tags=["Execution"],

)


# ============================================================
# POST /execute
# ============================================================

@router.post(

    "",

    response_model=ExecuteResponse,

)
def execute(

    request: ExecuteRequest,

    manager: AgentManager = Depends(
        get_agent_manager,
    ),

    context: AgentContext = Depends(
        get_agent_context,
    ),

):

    if not manager.contains(
        request.agent,
    ):

        raise HTTPException(

            status_code=404,

            detail=(
                f"Unknown agent "
                f"'{request.agent}'."
            ),

        )

    result = manager.execute_by_id(

        request.agent,

        context=context,

        **request.inputs,

    )

    if not result.success:

        raise HTTPException(

            status_code=500,

            detail=result.error
            or "Execution failed.",

        )

    return ExecuteResponse(

        success=True,

        message="Execution completed.",

        agent=request.agent,

        output=result.output,

        metadata=result.metadata,

    )