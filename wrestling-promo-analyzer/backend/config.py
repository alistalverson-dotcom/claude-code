"""
Configuration management for Wrestling Promo Analyzer
Loads settings from environment variables
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # ============================================================================
    # APPLICATION SETTINGS
    # ============================================================================
    APP_ENV: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production")

    # ============================================================================
    # DATABASE SETTINGS
    # ============================================================================
    DATABASE_URL: str = Field(
        default="postgresql://promo_admin:changeme123@postgres:5432/promo_analyzer"
    )
    POSTGRES_USER: str = Field(default="promo_admin")
    POSTGRES_PASSWORD: str = Field(default="changeme123")
    POSTGRES_DB: str = Field(default="promo_analyzer")

    # ============================================================================
    # REDIS & CELERY
    # ============================================================================
    REDIS_URL: str = Field(default="redis://redis:6379/0")
    CELERY_BROKER_URL: str = Field(default="redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://redis:6379/0")

    # ============================================================================
    # FILE UPLOAD SETTINGS
    # ============================================================================
    UPLOAD_DIR: str = Field(default="/app/uploads")
    MAX_UPLOAD_SIZE_MB: int = Field(default=500)
    ALLOWED_VIDEO_FORMATS: str = Field(default="mp4,mov,avi,mkv")

    @property
    def allowed_formats_list(self) -> List[str]:
        """Get allowed video formats as a list"""
        return [f".{fmt.strip()}" for fmt in self.ALLOWED_VIDEO_FORMATS.split(",")]

    @property
    def max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes"""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # ============================================================================
    # VIDEO PROCESSING
    # ============================================================================
    FFMPEG_PATH: str = Field(default="ffmpeg")
    WHISPER_MODEL: str = Field(default="base")
    WHISPER_DEVICE: str = Field(default="cpu")

    # ============================================================================
    # AI SETTINGS (Claude API)
    # ============================================================================
    ANTHROPIC_API_KEY: str = Field(default="")
    ANTHROPIC_MODEL: str = Field(default="claude-sonnet-4-20250514")
    ANTHROPIC_MAX_TOKENS: int = Field(default=4000)
    ANTHROPIC_TEMPERATURE: float = Field(default=0.7)

    # ============================================================================
    # CORS SETTINGS
    # ============================================================================
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:8000")

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # ============================================================================
    # LOGGING
    # ============================================================================
    LOG_LEVEL: str = Field(default="INFO")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()


# ============================================================================
# VALIDATION
# ============================================================================

def validate_settings():
    """Validate critical settings on startup"""
    errors = []

    # Check Anthropic API key
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "":
        errors.append("ANTHROPIC_API_KEY is not set")

    # Check database URL
    if "changeme" in settings.POSTGRES_PASSWORD.lower():
        errors.append("POSTGRES_PASSWORD should be changed from default")

    # Check upload directory exists
    if not os.path.exists(settings.UPLOAD_DIR):
        try:
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            os.makedirs(os.path.join(settings.UPLOAD_DIR, "processed"), exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create upload directory: {e}")

    # Check Whisper model is valid
    valid_whisper_models = ["tiny", "base", "small", "medium", "large"]
    if settings.WHISPER_MODEL not in valid_whisper_models:
        errors.append(
            f"WHISPER_MODEL must be one of {valid_whisper_models}, got {settings.WHISPER_MODEL}"
        )

    if errors:
        raise ValueError(
            f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        )


# ============================================================================
# ENVIRONMENT INFO
# ============================================================================

def print_settings():
    """Print non-sensitive settings for debugging"""
    print("=" * 60)
    print("WRESTLING PROMO ANALYZER - CONFIGURATION")
    print("=" * 60)
    print(f"Environment: {settings.APP_ENV}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"Database: {settings.POSTGRES_DB}")
    print(f"Upload Directory: {settings.UPLOAD_DIR}")
    print(f"Max Upload Size: {settings.MAX_UPLOAD_SIZE_MB}MB")
    print(f"Allowed Formats: {settings.ALLOWED_VIDEO_FORMATS}")
    print(f"Whisper Model: {settings.WHISPER_MODEL}")
    print(f"Claude Model: {settings.ANTHROPIC_MODEL}")
    print(f"CORS Origins: {settings.CORS_ORIGINS}")
    print(f"Anthropic API Key: {'✅ Set' if settings.ANTHROPIC_API_KEY else '❌ Missing'}")
    print("=" * 60)
