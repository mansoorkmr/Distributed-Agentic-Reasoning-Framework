"""
Distributed Agentic Reasoning Framework (DARF)

Request Logging Middleware
"""

from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Define logger specifically for the middleware layer
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Institutional-grade logging middleware with Correlation IDs.
    """

    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:
        
        # Generate a unique ID for this specific request
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()
        
        # Inject the ID into the request state
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error("Request %s failed: %s", request_id, str(e))
            raise e
        finally:
            elapsed = (time.perf_counter() - start_time) * 1000
            logger.info(
                "ID=%s | %s %s -> %d (%.2f ms)",
                request_id,
                request.method,
                request.url.path,
                response.status_code,
                elapsed,
            )
            
        return response