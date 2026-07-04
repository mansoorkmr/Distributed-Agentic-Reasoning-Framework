"""
Distributed Agentic Reasoning Framework (DARF)

FastAPI Response Models
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# BASE RESPONSE
# ============================================================

class APIResponse(BaseModel):
    """
    Base response model.
    """

    success: bool = True

    message: str = "OK"

    model_config = ConfigDict(
        extra="forbid",
    )


# ============================================================
# CHAT RESPONSE
# ============================================================

class ChatResponse(APIResponse):
    """
    Response returned by POST /chat
    """

    response: str

    agent: str = "llm"

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


# ============================================================
# EXECUTE RESPONSE
# ============================================================

class ExecuteResponse(APIResponse):
    """
    Response returned by POST /execute
    """

    agent: str

    output: Any = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


# ============================================================
# MEMORY RESPONSE
# ============================================================

class MemoryResponse(APIResponse):
    """
    Response returned by GET /memory
    """

    memory: dict[str, Any] = Field(
        default_factory=dict,
    )


# ============================================================
# TOOL RESPONSE
# ============================================================

class ToolResponse(APIResponse):
    """
    Response returned by tool execution.
    """

    tool: str

    output: Any = None


# ============================================================
# AGENTS RESPONSE
# ============================================================

class AgentsResponse(APIResponse):
    """
    Response returned by GET /agents
    """

    agents: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# ERROR RESPONSE
# ============================================================

class ErrorResponse(APIResponse):
    """
    Standard API error response.
    """

    success: bool = False

    error: str