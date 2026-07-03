"""
Distributed Agentic Reasoning Framework (DARF)

Global Exception Handlers
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse

# Use the established DARF logger
logger = logging.getLogger("DARF")

# ============================================================
# HTTP EXCEPTION HANDLER
# ============================================================

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handles standard HTTP exceptions (404, 403, etc.).
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.warning(
        "HTTP Exception: [%s] %d - %s", 
        request_id, exc.status_code, exc.detail
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": "Request failed.",
            "error": exc.detail,
            "request_id": request_id,
        },
    )

# ============================================================
# UNHANDLED EXCEPTION HANDLER
# ============================================================

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global catch-all for unhandled exceptions to prevent server crashes 
    and maintain security by hiding internal implementation details.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Log the full stack trace for internal debugging
    logger.exception(
        "Unhandled exception | ID=%s | Path=%s", 
        request_id, request.url.path, exc_info=exc
    )

    # Return a generic error message to the client for security
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error.",
            "error": "An unexpected error occurred. Please contact support.",
            "request_id": request_id,
        },
    )

# ============================================================
# REGISTRATION
# ============================================================

def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all global exception handlers to the FastAPI app.
    """
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)