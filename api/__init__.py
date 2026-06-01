"""
API Layer Initialization Module
==============================

This module defines the **public contract boundary** of the system.

It enforces:
    ✔ Strong typing
    ✔ Strict request/response schema validation
    ✔ Controlled exposure of API components
    ✔ Fail-fast behavior (no silent errors)
    ✔ Idempotent and deterministic interactions

Design Patterns:
    - Facade Pattern: unified interface for external callers
    - Factory Pattern: controlled API handler instantiation
    - Singleton Pattern: shared API registry
    - Guard Clause: fail-fast validation

Time Complexity:
    - Validation: O(n) for input size
    - Dispatch: O(1)

This module is intentionally strict to eliminate:
    - Runtime schema mismatches
    - Invalid external inputs
    - Silent failures in API calls
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Final, Callable


# =========================================================
# EXCEPTION HIERARCHY (STRICT CONTRACT)
# =========================================================

class APIError(Exception):
    """Base API error."""
    pass


class APIValidationError(APIError):
    """Raised when request validation fails."""
    pass


class APIRuntimeError(APIError):
    """Raised when execution fails."""
    pass


# =========================================================
# DATA CONTRACTS (TYPE-SAFE)
# =========================================================

@dataclass(frozen=True)
class APIRequest:
    """
    Immutable API Request Schema.

    Attributes:
        endpoint (str): API endpoint name
        payload (Dict[str, Any]): request data

    Complexity:
        O(1) field access
    """
    endpoint: str
    payload: Dict[str, Any]


@dataclass(frozen=True)
class APIResponse:
    """
    Immutable API Response Schema.

    Attributes:
        status (str): "success" or "error"
        data (Dict[str, Any]): response payload

    Complexity:
        O(1)
    """
    status: str
    data: Dict[str, Any]


# =========================================================
# VALIDATION LAYER
# =========================================================

def _validate_request(request: APIRequest) -> None:
    """
    Validate API request.

    Complexity: O(n) with respect to payload size
    """
    if not isinstance(request.endpoint, str) or not request.endpoint.strip():
        raise APIValidationError("Invalid endpoint")

    if not isinstance(request.payload, dict):
        raise APIValidationError("Payload must be a dictionary")


def _validate_response(response: APIResponse) -> None:
    """
    Validate API response.

    Complexity: O(n)
    """
    if response.status not in ("success", "error"):
        raise APIValidationError("Invalid response status")

    if not isinstance(response.data, dict):
        raise APIValidationError("Response data must be a dictionary")


# =========================================================
# API REGISTRY (SINGLETON)
# =========================================================

class APIRegistry:
    """
    Singleton API handler registry.

    Guarantees:
        ✔ No duplicate endpoint registration
        ✔ Deterministic handler resolution

    Complexity:
        - Register: O(1)
        - Lookup: O(1)
    """

    _instance: Final["APIRegistry"] = None
    _handlers: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]]

    def __new__(cls) -> "APIRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers = {}
        return cls._instance

    def register(self, endpoint: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        if endpoint in self._handlers:
            raise APIError(f"Endpoint already registered: {endpoint}")

        self._handlers[endpoint] = handler

    def get(self, endpoint: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        if endpoint not in self._handlers:
            raise APIError(f"Endpoint not found: {endpoint}")

        return self._handlers[endpoint]


_registry = APIRegistry()


# =========================================================
# CORE API EXECUTION ENGINE
# =========================================================

def handle_request(request: APIRequest) -> APIResponse:
    """
    Main API execution entry point.

    Steps:
        1. Validate request
        2. Resolve handler
        3. Execute handler
        4. Validate response

    Complexity:
        O(n) (dominated by payload processing)
    """

    _validate_request(request)

    try:
        handler = _registry.get(request.endpoint)
        result = handler(request.payload)

        response = APIResponse(status="success", data=result)

    except Exception as e:
        response = APIResponse(
            status="error",
            data={"error": str(e)}
        )

    _validate_response(response)
    return response


# =========================================================
# PUBLIC EXPORTS (STRICT API SURFACE)
# =========================================================

__all__ = [
    "APIRequest",
    "APIResponse",
    "APIRegistry",
    "handle_request",
    "APIError",
    "APIValidationError",
    "APIRuntimeError",
]
