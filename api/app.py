"""
Distributed Agentic Reasoning Framework (DARF)

Main FastAPI Application
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import APIConfig
# Integrated Middleware
from api.middleware import (
    RequestLoggingMiddleware,
    register_exception_handlers,
)

from api.routes.chat import router as chat_router
from api.routes.execute import router as execute_router
from api.routes.agents import router as agents_router
from api.routes.memory import router as memory_router
from api.routes.tools import router as tools_router

# System Initialization
from bootstrap import initialize


# ============================================================
# CONFIGURATION
# ============================================================

config = APIConfig()


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title=config.title,
    description=config.description,
    version=config.version,
    docs_url=config.docs_url,
    redoc_url=config.redoc_url,
    openapi_url=config.openapi_url,
)


# ============================================================
# MIDDLEWARE
# ============================================================

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=config.cors_methods,
    allow_headers=config.cors_headers,
)

# 2. Request Logging Middleware (Integrated)
app.add_middleware(RequestLoggingMiddleware)


# ============================================================
# LIFECYCLE EVENTS
# ============================================================

@app.on_event("startup")
async def startup_event() -> None:
    """
    Initialize the DARF application architecture.
    Bootstraps the registry, agents, and LLM providers 
    before accepting API traffic.
    """
    initialize()


# ============================================================
# ROUTES & HANDLERS
# ============================================================

# Register API Routers
app.include_router(chat_router)
app.include_router(execute_router)
app.include_router(agents_router)
app.include_router(memory_router)
app.include_router(tools_router)

# Register Global Exception Handlers (Integrated)
register_exception_handlers(app)


# ============================================================
# ROOT & HEALTH
# ============================================================

@app.get("/", tags=["Root"])
def root():
    return {
        "name": config.title,
        "version": config.version,
        "status": "running",
        "docs": config.docs_url,
    }

@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "healthy",
        "version": config.version,
    }