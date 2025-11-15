"""
Logging middleware for FastAPI
Logs all API requests with timing and status codes
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from utils.logging_config import log_api_request, get_logger

logger = get_logger(__name__)


class APILoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all API requests

    Logs:
    - Request method and path
    - Response status code
    - Request duration
    - Client IP address
    - Query parameters (optional)
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """Process request and log it"""

        # Start timer
        start_time = time.time()

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        if forwarded := request.headers.get("X-Forwarded-For"):
            client_ip = forwarded.split(",")[0].strip()

        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # Log exception
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": client_ip,
                    "duration_ms": round(duration_ms, 2),
                    "error": str(e),
                },
                exc_info=True
            )
            raise

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Get query params (exclude sensitive data)
        query_params = dict(request.query_params) if request.query_params else None

        # Log the request
        log_api_request(
            method=request.method,
            path=request.url.path,
            status_code=status_code,
            duration_ms=duration_ms,
            client_ip=client_ip,
            query_params=query_params,
        )

        return response
