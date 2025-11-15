"""
Logging configuration for Wrestling Promo Analyzer
Provides structured JSON logging with file rotation
"""

import logging
import logging.handlers
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs as JSON

    Format includes:
    - timestamp: ISO format
    - level: Log level (INFO, ERROR, etc.)
    - logger: Logger name
    - message: Log message
    - extra: Any additional context
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string"""

        # Base log data
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        # Add extra fields from record
        # Exclude standard LogRecord attributes
        skip_fields = {
            "name", "msg", "args", "created", "filename", "funcName",
            "levelname", "levelno", "lineno", "module", "msecs",
            "message", "pathname", "process", "processName", "relativeCreated",
            "thread", "threadName", "exc_info", "exc_text", "stack_info",
        }

        for key, value in record.__dict__.items():
            if key not in skip_fields and not key.startswith("_"):
                log_data[key] = value

        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """
    Colored console formatter for better readability in development

    Colors:
    - DEBUG: Cyan
    - INFO: Green
    - WARNING: Yellow
    - ERROR: Red
    - CRITICAL: Red + Bold
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[1;31m", # Bold Red
        "RESET": "\033[0m",       # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log with colors"""
        # Get color for level
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

        # Format message
        message = record.getMessage()

        # Add exception if present
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            message = f"{message}\n{exc_text}"

        return f"{color}[{timestamp}] {record.levelname:8s}{reset} {record.name:30s} {message}"


def setup_logging(
    log_dir: str = "logs",
    log_level: str = "INFO",
    enable_console: bool = True,
    enable_file: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Setup application-wide logging configuration

    Args:
        log_dir: Directory for log files
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_console: Whether to log to console
        enable_file: Whether to log to files
        max_bytes: Maximum size of each log file before rotation
        backup_count: Number of backup files to keep

    Creates log files:
    - app.log: All application logs (JSON format)
    - error.log: ERROR and CRITICAL only (JSON format)
    - celery.log: Celery worker logs (JSON format)
    """

    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers = []

    # ========================================================================
    # CONSOLE HANDLER (Development)
    # ========================================================================

    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        # Use colored formatter for console
        console_formatter = ColoredConsoleFormatter()
        console_handler.setFormatter(console_formatter)

        root_logger.addHandler(console_handler)

    # ========================================================================
    # FILE HANDLER - All Logs (JSON)
    # ========================================================================

    if enable_file:
        # Rotating file handler for all logs
        app_log_file = log_path / "app.log"
        app_handler = logging.handlers.RotatingFileHandler(
            filename=str(app_log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        app_handler.setLevel(logging.DEBUG)

        # Use JSON formatter for files
        json_formatter = JSONFormatter()
        app_handler.setFormatter(json_formatter)

        root_logger.addHandler(app_handler)

    # ========================================================================
    # FILE HANDLER - Errors Only (JSON)
    # ========================================================================

    if enable_file:
        # Rotating file handler for errors
        error_log_file = log_path / "error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            filename=str(error_log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(json_formatter)

        root_logger.addHandler(error_handler)

    # ========================================================================
    # FILE HANDLER - Celery Workers (JSON)
    # ========================================================================

    if enable_file:
        # Separate log file for Celery
        celery_logger = logging.getLogger("celery")
        celery_log_file = log_path / "celery.log"

        celery_handler = logging.handlers.RotatingFileHandler(
            filename=str(celery_log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        celery_handler.setLevel(logging.DEBUG)
        celery_handler.setFormatter(json_formatter)

        celery_logger.addHandler(celery_handler)

    # ========================================================================
    # CONFIGURE EXTERNAL LIBRARIES
    # ========================================================================

    # Reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "log_dir": str(log_path),
            "log_level": log_level,
            "console_enabled": enable_console,
            "file_enabled": enable_file,
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("Processing video", extra={"video_id": "123"})
    """
    return logging.getLogger(name)


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    client_ip: str = None,
    **kwargs
) -> None:
    """
    Log an API request with structured data

    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        client_ip: Client IP address
        **kwargs: Additional context to log
    """
    logger = get_logger("api")

    extra = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
        "client_ip": client_ip,
        **kwargs
    }

    # Determine log level based on status code
    if status_code >= 500:
        logger.error(f"{method} {path} - {status_code}", extra=extra)
    elif status_code >= 400:
        logger.warning(f"{method} {path} - {status_code}", extra=extra)
    else:
        logger.info(f"{method} {path} - {status_code}", extra=extra)


def log_task_event(
    task_name: str,
    event_type: str,
    video_id: str = None,
    **kwargs
) -> None:
    """
    Log a Celery task event with structured data

    Args:
        task_name: Name of the task
        event_type: Event type (started, completed, failed, retry)
        video_id: Video ID being processed
        **kwargs: Additional context to log
    """
    logger = get_logger("celery.task")

    extra = {
        "task_name": task_name,
        "event_type": event_type,
        "video_id": video_id,
        **kwargs
    }

    message = f"Task {task_name} - {event_type}"

    if event_type == "failed":
        logger.error(message, extra=extra)
    elif event_type == "retry":
        logger.warning(message, extra=extra)
    else:
        logger.info(message, extra=extra)


# Example structured logging helpers
def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **context
) -> None:
    """
    Log a message with additional context

    Args:
        logger: Logger instance
        level: Log level (info, warning, error, etc.)
        message: Log message
        **context: Additional context fields

    Example:
        log_with_context(
            logger, "info", "Video uploaded",
            video_id="123",
            file_size=1024000,
            duration=45.5
        )
    """
    log_method = getattr(logger, level.lower())
    log_method(message, extra=context)
