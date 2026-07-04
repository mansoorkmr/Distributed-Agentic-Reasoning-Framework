"""
Distributed Agentic Reasoning Framework (DARF)

FastAPI Request Models
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# CHAT
# ============================================================

class ChatRequest(BaseModel):
    """
    POST /chat
    """

    prompt: str = Field(
        ...,
        min_length=1,
        description="User prompt.",
    )

    session_id: str | None = None

    temperature: float = 0.7

    max_tokens: int = 1024

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    model_config = ConfigDict(
        extra="forbid",
    )


# ============================================================
# EXECUTION
# ============================================================

class ExecuteRequest(BaseModel):
    """
    POST /execute
    """

    agent: str = Field(
        ...,
        description="Agent ID",
    )

    inputs: dict[str, Any] = Field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    model_config = ConfigDict(
        extra="forbid",
    )


# ============================================================
# MEMORY
# ============================================================

class MemoryRequest(BaseModel):
    """
    Memory operations.
    """

    operation: str

    key: str

    value: Any | None = None

    model_config = ConfigDict(
        extra="forbid",
    )


# ============================================================
# TOOL
# ============================================================

class ToolRequest(BaseModel):
    """
    Tool execution.
    """

    tool: str

    arguments: dict[str, Any] = Field(
        default_factory=dict,
    )

    model_config = ConfigDict(
        extra="forbid",
    )