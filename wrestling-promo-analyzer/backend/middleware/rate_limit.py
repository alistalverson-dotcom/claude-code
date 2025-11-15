"""
Rate limiting middleware for FastAPI
Prevents abuse by limiting requests per IP address
"""

from typing import Callable
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio


class RateLimiter:
    """
    Simple in-memory rate limiter

    For production, consider using Redis-backed rate limiting.
    This implementation uses local memory and won't work across multiple workers.
    """

    def __init__(self):
        # Store: {ip_address: [(timestamp, endpoint), ...]}
        self.requests = defaultdict(list)
        self.lock = asyncio.Lock()

    async def cleanup_old_requests(self):
        """Remove expired request records to prevent memory bloat"""
        async with self.lock:
            current_time = datetime.utcnow()
            for ip, records in list(self.requests.items()):
                # Remove records older than 1 hour
                cutoff_time = current_time - timedelta(hours=1)
                self.requests[ip] = [
                    (ts, endpoint) for ts, endpoint in records
                    if ts > cutoff_time
                ]
                # Remove IP if no recent requests
                if not self.requests[ip]:
                    del self.requests[ip]

    async def is_rate_limited(
        self,
        ip: str,
        endpoint: str,
        max_requests: int,
        window_minutes: int
    ) -> tuple[bool, dict]:
        """
        Check if IP has exceeded rate limit for endpoint

        Args:
            ip: Client IP address
            endpoint: API endpoint path
            max_requests: Maximum requests allowed in window
            window_minutes: Time window in minutes

        Returns:
            (is_limited, info_dict) where info_dict contains:
                - requests_made: Number of requests in window
                - requests_remaining: Requests remaining
                - reset_at: When the limit resets
        """
        async with self.lock:
            current_time = datetime.utcnow()
            cutoff_time = current_time - timedelta(minutes=window_minutes)

            # Get recent requests for this IP and endpoint
            recent_requests = [
                ts for ts, ep in self.requests.get(ip, [])
                if ep == endpoint and ts > cutoff_time
            ]

            requests_made = len(recent_requests)
            requests_remaining = max(0, max_requests - requests_made)
            is_limited = requests_made >= max_requests

            # Calculate reset time (when oldest request expires)
            reset_at = None
            if recent_requests:
                oldest_request = min(recent_requests)
                reset_at = oldest_request + timedelta(minutes=window_minutes)

            info = {
                "requests_made": requests_made,
                "requests_remaining": requests_remaining,
                "reset_at": reset_at.isoformat() if reset_at else None,
            }

            return is_limited, info

    async def record_request(self, ip: str, endpoint: str):
        """Record a request from an IP to an endpoint"""
        async with self.lock:
            current_time = datetime.utcnow()
            self.requests[ip].append((current_time, endpoint))

            # Cleanup periodically (every 100 requests)
            if sum(len(records) for records in self.requests.values()) % 100 == 0:
                await self.cleanup_old_requests()


# Global rate limiter instance
rate_limiter = RateLimiter()


# Rate limit configurations for different endpoints
RATE_LIMITS = {
    "/api/v1/videos/upload": {
        "max_requests": 5,
        "window_minutes": 60,
        "message": "Upload limit exceeded. Maximum 5 uploads per hour.",
    },
    "/api/v1/videos": {
        "max_requests": 100,
        "window_minutes": 60,
        "message": "Too many requests. Please slow down.",
    },
}


def get_client_ip(request: Request) -> str:
    """
    Extract client IP from request

    Checks X-Forwarded-For header first (for proxies),
    then falls back to client host.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For can be a comma-separated list
        return forwarded.split(",")[0].strip()

    return request.client.host if request.client else "unknown"


async def check_rate_limit(request: Request):
    """
    Middleware function to check rate limits

    Usage:
        @app.post("/api/v1/videos/upload", dependencies=[Depends(check_rate_limit)])
        async def upload_video(...):
            ...
    """
    # Get endpoint path (without query parameters)
    endpoint = request.url.path

    # Check if this endpoint has rate limiting
    if endpoint not in RATE_LIMITS:
        return  # No rate limit for this endpoint

    config = RATE_LIMITS[endpoint]
    client_ip = get_client_ip(request)

    # Check if rate limited
    is_limited, info = await rate_limiter.is_rate_limited(
        ip=client_ip,
        endpoint=endpoint,
        max_requests=config["max_requests"],
        window_minutes=config["window_minutes"],
    )

    if is_limited:
        # Add rate limit headers to response
        reset_at = info.get("reset_at", "unknown")

        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": config["message"],
                "requests_made": info["requests_made"],
                "requests_remaining": 0,
                "reset_at": reset_at,
            },
            headers={
                "X-RateLimit-Limit": str(config["max_requests"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": reset_at,
                "Retry-After": "3600",  # Retry after 1 hour
            },
        )

    # Record this request
    await rate_limiter.record_request(client_ip, endpoint)

    # Add rate limit info to response headers (for successful requests)
    # Note: This requires middleware to add headers after response
    request.state.rate_limit_info = {
        "limit": config["max_requests"],
        "remaining": info["requests_remaining"],
        "reset": info.get("reset_at"),
    }


class RateLimitHeaderMiddleware:
    """
    Middleware to add rate limit headers to all responses

    This helps clients know their rate limit status even for successful requests.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # Create a wrapper to capture response
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Check if request has rate limit info
                request = scope.get("state", {})
                rate_limit_info = getattr(request, "rate_limit_info", None)

                if rate_limit_info:
                    # Add rate limit headers
                    headers = list(message.get("headers", []))
                    headers.extend([
                        (b"x-ratelimit-limit", str(rate_limit_info["limit"]).encode()),
                        (b"x-ratelimit-remaining", str(rate_limit_info["remaining"]).encode()),
                    ])
                    if rate_limit_info.get("reset"):
                        headers.append((b"x-ratelimit-reset", rate_limit_info["reset"].encode()))

                    message["headers"] = headers

            await send(message)

        return await self.app(scope, receive, send_wrapper)
