# Rate Limiting

Rate limiting prevents abuse of the Wrestling Promo Analyzer API by restricting the number of requests from a single IP address within a time window.

## Overview

The rate limiting system uses an in-memory store to track requests per IP address. For each protected endpoint, limits are enforced based on:
- **IP Address**: Identified from request headers (X-Forwarded-For or direct connection)
- **Endpoint**: Specific API path
- **Time Window**: Rolling time window (e.g., 60 minutes)

## Current Limits

### Video Upload Endpoint

```
POST /api/v1/videos/upload
Limit: 5 uploads per hour per IP
```

This prevents users from:
- Overwhelming the processing pipeline
- Consuming excessive API costs
- Abusing free tier limits

### Other Endpoints

```
GET /api/v1/videos
Limit: 100 requests per hour per IP
```

General API endpoints have higher limits to allow normal browsing.

## How It Works

### 1. Request Tracking

Every request to a rate-limited endpoint is tracked:
```python
# Request recorded with:
{
    "ip_address": "192.168.1.100",
    "endpoint": "/api/v1/videos/upload",
    "timestamp": "2025-01-15T10:30:00Z"
}
```

### 2. Limit Checking

Before processing a request:
1. Count recent requests from the same IP to the same endpoint
2. If count >= limit, reject with 429 Too Many Requests
3. If count < limit, allow request and record it

### 3. Response Headers

All responses include rate limit headers:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 2025-01-15T11:30:00Z
```

When limit is exceeded:

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 2025-01-15T11:30:00Z
Retry-After: 3600

{
  "detail": {
    "error": "Rate limit exceeded",
    "message": "Upload limit exceeded. Maximum 5 uploads per hour.",
    "requests_made": 5,
    "requests_remaining": 0,
    "reset_at": "2025-01-15T11:30:00Z"
  }
}
```

## Configuration

Rate limits are configured in `backend/middleware/rate_limit.py`:

```python
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
```

### Customizing Limits

To change limits for an endpoint:

```python
RATE_LIMITS = {
    "/api/v1/videos/upload": {
        "max_requests": 10,  # Allow 10 uploads instead of 5
        "window_minutes": 30,  # Per 30 minutes instead of 60
        "message": "Upload limit exceeded. Maximum 10 uploads per 30 minutes.",
    },
}
```

### Adding New Limits

To add rate limiting to a new endpoint:

1. Add configuration:
```python
RATE_LIMITS = {
    "/api/v1/my-endpoint": {
        "max_requests": 50,
        "window_minutes": 60,
        "message": "Too many requests to this endpoint.",
    },
}
```

2. Apply to endpoint:
```python
@app.post("/api/v1/my-endpoint", dependencies=[Depends(check_rate_limit)])
async def my_endpoint(...):
    ...
```

## Frontend Integration

The frontend should handle 429 responses gracefully:

```typescript
try {
  const response = await uploadVideo(formData)
} catch (error) {
  if (error.status === 429) {
    const resetTime = new Date(error.data.reset_at)
    const waitMinutes = Math.ceil((resetTime - new Date()) / 60000)

    showError(
      `Upload limit exceeded. Please try again in ${waitMinutes} minutes.`
    )
  }
}
```

Display rate limit info to users:

```typescript
// Check response headers
const limit = response.headers.get('X-RateLimit-Limit')
const remaining = response.headers.get('X-RateLimit-Remaining')

if (remaining < 2) {
  showWarning(`You have ${remaining} uploads remaining this hour.`)
}
```

## Implementation Details

### In-Memory Storage

The current implementation uses in-memory Python dictionaries:

**Pros:**
- Simple, no external dependencies
- Fast lookups
- Good for single-worker deployments

**Cons:**
- Doesn't persist across restarts
- Doesn't work across multiple workers
- Memory usage grows with traffic

### For Production

Consider upgrading to Redis-backed rate limiting:

```python
import redis
from fastapi_limiter import FastAPILimiter

# Initialize Redis
redis_client = redis.Redis(host="localhost", port=6379)
await FastAPILimiter.init(redis_client)

# Apply limits
from fastapi_limiter.depends import RateLimiter

@app.post("/api/v1/videos/upload", dependencies=[Depends(RateLimiter(times=5, hours=1))])
async def upload_video(...):
    ...
```

Benefits:
- Shared state across workers
- Persists across restarts
- Better performance at scale
- More flexible configurations

### IP Detection

IP addresses are detected using:

1. **X-Forwarded-For** header (if behind proxy/load balancer)
2. **Direct client IP** (if connecting directly)

For deployment behind Nginx/CloudFlare:

```python
def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host
```

**Security Note:** X-Forwarded-For can be spoofed. In production:
- Trust proxy headers only from known proxies
- Use X-Real-IP if available
- Consider using a reverse proxy that sets trusted headers

## Testing Rate Limits

### Manual Testing

Test the upload limit:

```bash
# Make 5 uploads
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/v1/videos/upload \
    -F "file=@test.mp4" \
    -F "promo_title=Test $i"
done

# 6th upload should fail with 429
curl -X POST http://localhost:8000/api/v1/videos/upload \
  -F "file=@test.mp4" \
  -F "promo_title=Test 6"
```

### Automated Testing

```python
import pytest
import requests

def test_upload_rate_limit():
    # Upload 5 times
    for i in range(5):
        response = requests.post(
            "http://localhost:8000/api/v1/videos/upload",
            files={"file": ("test.mp4", open("test.mp4", "rb"))},
        )
        assert response.status_code == 201

    # 6th upload should be rate limited
    response = requests.post(
        "http://localhost:8000/api/v1/videos/upload",
        files={"file": ("test.mp4", open("test.mp4", "rb"))},
    )
    assert response.status_code == 429
    assert "rate limit exceeded" in response.json()["detail"]["error"].lower()
```

## Monitoring

Track rate limit hits:

```python
# Add logging to rate_limit.py
import logging

logger = logging.getLogger(__name__)

if is_limited:
    logger.warning(
        f"Rate limit hit: IP={client_ip}, endpoint={endpoint}, "
        f"requests={info['requests_made']}"
    )
```

Common patterns to watch for:
- **Single IP hitting limits repeatedly**: Potential abuse
- **Many IPs hitting limits**: Limits may be too strict
- **No rate limit hits**: Limits may be too generous

## Bypassing Limits (Development)

For testing, you can temporarily disable rate limiting:

```python
# In rate_limit.py, add environment check
import os

if os.getenv("DISABLE_RATE_LIMITING") == "true":
    return  # Skip rate limiting

# Run with:
# DISABLE_RATE_LIMITING=true uvicorn main:app
```

Or add IP whitelist:

```python
WHITELISTED_IPS = ["127.0.0.1", "localhost"]

if client_ip in WHITELISTED_IPS:
    return  # Skip rate limiting for whitelisted IPs
```

## Future Enhancements

Potential improvements:

1. **User-based limits**: Rate limit by authenticated user instead of IP
2. **Sliding window**: More accurate rate limiting algorithm
3. **Distributed limits**: Redis backend for multi-worker deployments
4. **Custom limits per tier**: Different limits for free/paid users
5. **Automatic ban**: Temporarily ban IPs that repeatedly exceed limits
6. **Dashboard**: Admin UI to view and manage rate limits

## Troubleshooting

### "Rate limit exceeded" but I haven't uploaded recently

**Causes:**
- Shared IP address (office, VPN)
- Rate limit window hasn't expired yet
- Application restart (in-memory storage cleared)

**Solutions:**
- Wait for the reset time indicated in the error
- Use a different network connection
- Contact administrator for whitelist

### Rate limits not working

**Causes:**
- Middleware not registered
- Dependency not added to endpoint
- IP detection failing

**Debug:**
```python
# Add logging to see detected IPs
logger.info(f"Request from IP: {get_client_ip(request)}")
```

### Different workers have different limits

**Cause:**
- In-memory storage doesn't share between workers
- Each worker tracks limits independently

**Solution:**
- Upgrade to Redis-backed rate limiting
- Run single worker (development only)
