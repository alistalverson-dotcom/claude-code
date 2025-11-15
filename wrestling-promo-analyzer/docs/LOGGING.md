# Logging System

Comprehensive logging system for Wrestling Promo Analyzer with structured JSON logging, file rotation, and centralized configuration.

## Overview

The logging system captures:
- **API requests**: All HTTP requests with timing and status codes
- **Celery tasks**: Task lifecycle events (started, completed, failed, retry)
- **Application events**: Startup, shutdown, errors
- **Debug information**: For troubleshooting in development

## Log Files

All logs are stored in the `backend/logs/` directory:

### app.log
- **Content**: All application logs (INFO and above)
- **Format**: JSON (one line per log entry)
- **Rotation**: 10MB max size, 5 backup files
- **Use**: General application monitoring

### error.log
- **Content**: ERROR and CRITICAL logs only
- **Format**: JSON
- **Rotation**: 10MB max size, 5 backup files
- **Use**: Quick access to errors for debugging

### celery.log
- **Content**: Celery worker logs
- **Format**: JSON
- **Rotation**: 10MB max size, 5 backup files
- **Use**: Debugging task processing issues

## Log Format

### JSON Format (Files)

All file logs use structured JSON format for easy parsing:

```json
{
  "timestamp": "2025-01-15T10:30:45.123456Z",
  "level": "INFO",
  "logger": "api",
  "message": "GET /api/v1/videos - 200",
  "method": "GET",
  "path": "/api/v1/videos",
  "status_code": 200,
  "duration_ms": 45.23,
  "client_ip": "192.168.1.100"
}
```

### Console Format (Development)

Console logs use colored, human-readable format:

```
[10:30:45] INFO     api                            GET /api/v1/videos - 200
[10:30:46] ERROR    celery.task                   Task analyze_with_jake - failed
```

Colors:
- **DEBUG**: Cyan
- **INFO**: Green
- **WARNING**: Yellow
- **ERROR**: Red
- **CRITICAL**: Bold Red

## Common Log Patterns

### API Request Logs

```json
{
  "timestamp": "2025-01-15T10:30:45Z",
  "level": "INFO",
  "logger": "api",
  "message": "POST /api/v1/videos/upload - 201",
  "method": "POST",
  "path": "/api/v1/videos/upload",
  "status_code": 201,
  "duration_ms": 1234.56,
  "client_ip": "192.168.1.100",
  "query_params": null
}
```

### Task Event Logs

```json
{
  "timestamp": "2025-01-15T10:31:00Z",
  "level": "INFO",
  "logger": "celery.task",
  "message": "Task analyze_with_jake - completed",
  "task_name": "analyze_with_jake",
  "event_type": "completed",
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "duration": 45.2,
  "cost_usd": 0.0345
}
```

### Error Logs

```json
{
  "timestamp": "2025-01-15T10:32:00Z",
  "level": "ERROR",
  "logger": "celery.task",
  "message": "FFmpeg extraction failed",
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "exception": {
    "type": "FFmpegError",
    "message": "FFprobe failed: Invalid data found",
    "traceback": "Traceback (most recent call last):\n  File..."
  }
}
```

## Configuration

### Environment Variables

Add to `.env` file:

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Code Configuration

In `backend/main.py`:

```python
from utils.logging_config import setup_logging

setup_logging(
    log_dir="logs",          # Directory for log files
    log_level="INFO",        # Minimum level to log
    enable_console=True,     # Log to console (development)
    enable_file=True,        # Log to files (production)
    max_bytes=10485760,      # 10MB per file
    backup_count=5,          # Keep 5 old files
)
```

## Usage Examples

### Basic Logging

```python
from utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Processing video")
logger.warning("Low disk space")
logger.error("Upload failed", exc_info=True)
```

### Structured Logging

Add extra context to logs:

```python
logger.info(
    "Video uploaded successfully",
    extra={
        "video_id": "123",
        "file_size": 1024000,
        "duration": 45.5,
        "user_id": "user_456"
    }
)
```

Produces:

```json
{
  "timestamp": "2025-01-15T10:30:45Z",
  "level": "INFO",
  "logger": "main",
  "message": "Video uploaded successfully",
  "video_id": "123",
  "file_size": 1024000,
  "duration": 45.5,
  "user_id": "user_456"
}
```

### API Request Logging

Automatic via middleware - no code needed:

```python
# Requests are automatically logged by APILoggingMiddleware
```

### Task Logging

```python
from utils.logging_config import log_task_event

log_task_event(
    task_name="analyze_with_jake",
    event_type="started",
    video_id="123",
    extra_data={"model": "claude-3-5-sonnet"}
)
```

### Logging with Context Helper

```python
from utils.logging_config import log_with_context

log_with_context(
    logger, "info", "Processing completed",
    video_id="123",
    processing_time=45.2,
    tokens_used=4500
)
```

## Log Levels

### DEBUG
- Detailed information for diagnosing problems
- Only enabled in development
- Examples: Variable values, function calls

```python
logger.debug("Transcript segments", extra={"count": len(segments)})
```

### INFO
- Confirmation that things are working
- Default level for production
- Examples: Request completed, task started

```python
logger.info("Video processing started")
```

### WARNING
- Something unexpected but not an error
- Application continues normally
- Examples: Rate limit approaching, deprecated feature used

```python
logger.warning("Upload queue is 80% full")
```

### ERROR
- Application failed to perform a function
- Requires investigation
- Examples: Database query failed, API call failed

```python
logger.error("Failed to save video", exc_info=True)
```

### CRITICAL
- Serious error, application may not continue
- Immediate attention required
- Examples: Database down, out of memory

```python
logger.critical("Cannot connect to database")
```

## Analyzing Logs

### View Recent Logs

```bash
# Last 50 lines
tail -n 50 backend/logs/app.log

# Follow logs in real-time
tail -f backend/logs/app.log

# View error logs only
cat backend/logs/error.log
```

### Parse JSON Logs

Using `jq` (JSON processor):

```bash
# Pretty print
cat backend/logs/app.log | jq '.'

# Filter by level
cat backend/logs/app.log | jq 'select(.level == "ERROR")'

# Filter by logger
cat backend/logs/app.log | jq 'select(.logger == "celery.task")'

# Extract specific fields
cat backend/logs/app.log | jq '{time: .timestamp, msg: .message}'

# Count errors by type
cat backend/logs/error.log | jq -r '.exception.type' | sort | uniq -c
```

### Search Logs

```bash
# Find all logs for a specific video
grep "video_id_here" backend/logs/app.log

# Find failed uploads
grep "upload.*failed" backend/logs/app.log

# Find slow requests (> 1000ms)
cat backend/logs/app.log | jq 'select(.duration_ms > 1000)'
```

### Log Statistics

```bash
# Count log levels
cat backend/logs/app.log | jq -r '.level' | sort | uniq -c

# Average API response time
cat backend/logs/app.log | jq -s 'map(select(.duration_ms)) | map(.duration_ms) | add/length'

# Most accessed endpoints
cat backend/logs/app.log | jq -r '.path' | sort | uniq -c | sort -rn | head -10
```

## Log Rotation

Logs automatically rotate when they reach 10MB:

```
logs/
├── app.log           # Current log
├── app.log.1         # Previous (most recent)
├── app.log.2
├── app.log.3
├── app.log.4
└── app.log.5         # Oldest backup
```

When `app.log` reaches 10MB:
1. `app.log.5` is deleted
2. Other backups shift: `.4` → `.5`, `.3` → `.4`, etc.
3. `app.log` → `app.log.1`
4. New `app.log` starts fresh

## Centralized Logging (Production)

For production deployments, send logs to centralized service:

### ELK Stack (Elasticsearch, Logstash, Kibana)

```python
# Add Elasticsearch handler
from elasticsearch import Elasticsearch
from cmreslogging.handlers import CMRESHandler

es = Elasticsearch(["http://localhost:9200"])
handler = CMRESHandler(hosts=["localhost:9200"], index_name="promo-analyzer")
logger.addHandler(handler)
```

### Cloud Services

**AWS CloudWatch:**
```python
import watchtower

handler = watchtower.CloudWatchLogHandler(log_group="promo-analyzer")
logger.addHandler(handler)
```

**Google Cloud Logging:**
```python
from google.cloud import logging as gcp_logging

client = gcp_logging.Client()
handler = client.get_default_handler()
logger.addHandler(handler)
```

## Best Practices

### DO

✅ **Use structured logging with context:**
```python
logger.info("Video uploaded", extra={"video_id": "123", "size": 1024})
```

✅ **Log at appropriate levels:**
```python
logger.info("Normal operation")
logger.error("Something failed", exc_info=True)
```

✅ **Include exc_info for errors:**
```python
try:
    process_video()
except Exception as e:
    logger.error("Processing failed", exc_info=True)
```

✅ **Use specific logger names:**
```python
logger = get_logger(__name__)  # Uses module name
```

### DON'T

❌ **Don't log sensitive data:**
```python
# BAD - Logs passwords!
logger.info("User login", extra={"password": password})

# GOOD - Omit sensitive fields
logger.info("User login", extra={"user_id": user_id})
```

❌ **Don't log in loops:**
```python
# BAD - Creates thousands of logs
for item in items:
    logger.info(f"Processing {item}")

# GOOD - Log summary
logger.info(f"Processing {len(items)} items")
```

❌ **Don't use print() statements:**
```python
# BAD
print("Debug info")

# GOOD
logger.debug("Debug info")
```

## Troubleshooting

### Logs not appearing

**Check permissions:**
```bash
ls -la backend/logs/
chmod 755 backend/logs/
```

**Check log level:**
```python
# Ensure level is set correctly
setup_logging(log_level="DEBUG")  # Most verbose
```

**Check logger configuration:**
```python
import logging
print(logging.root.level)  # Should show level number
print(logging.root.handlers)  # Should show handlers
```

### Log files too large

**Adjust rotation settings:**
```python
setup_logging(
    max_bytes=5 * 1024 * 1024,  # 5MB instead of 10MB
    backup_count=3,  # Keep only 3 backups
)
```

**Archive old logs:**
```bash
# Compress old logs
gzip backend/logs/*.log.[1-5]

# Archive to external storage
tar -czf logs-$(date +%Y%m%d).tar.gz backend/logs/*.log.gz
mv logs-*.tar.gz /archive/
```

### Performance issues

Logging shouldn't impact performance significantly, but if needed:

**Reduce console logging in production:**
```python
setup_logging(enable_console=False)  # Files only
```

**Increase log level:**
```python
setup_logging(log_level="WARNING")  # Less verbose
```

**Use asynchronous logging:**
```python
from concurrent_log_handler import ConcurrentRotatingFileHandler

handler = ConcurrentRotatingFileHandler("logs/app.log")
```

## Monitoring & Alerts

Set up alerts for critical errors:

```python
# Example: Send email on critical errors
import smtplib
from logging.handlers import SMTPHandler

smtp_handler = SMTPHandler(
    mailhost=("smtp.example.com", 587),
    fromaddr="alerts@example.com",
    toaddrs=["admin@example.com"],
    subject="Critical Error in Promo Analyzer",
)
smtp_handler.setLevel(logging.CRITICAL)
logger.addHandler(smtp_handler)
```

Or integrate with monitoring services:
- **Sentry**: Error tracking and alerting
- **Datadog**: Full observability platform
- **New Relic**: Application performance monitoring
- **PagerDuty**: Incident management and alerts
