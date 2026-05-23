"""
constants.py - Application-wide constants and magic numbers

Centralize all constant values used throughout the application
for easy maintenance and tuning.
"""
from __future__ import annotations


# ─────────────────────────────────────────────────────────────────────────────
#  Text Processing
# ─────────────────────────────────────────────────────────────────────────────
CHUNKER_DEFAULT_CHUNK_SIZE: int = 500
"""Default number of words per chunk."""

CHUNKER_DEFAULT_OVERLAP: int = 50
"""Default number of words to overlap between chunks."""

CHUNKER_MAX_BYTES: int = 3900
"""Maximum bytes per chunk for Oracle VARCHAR2(4000)."""

CHUNKER_SUPPORTED_EXTENSIONS: tuple = (".pdf", ".docx", ".txt", ".md")
"""File extensions supported for ingestion."""

# ─────────────────────────────────────────────────────────────────────────────
#  Database Constraints
# ─────────────────────────────────────────────────────────────────────────────
DB_CONNECTION_POOL_MIN: int = 1
"""Minimum connections in pool."""

DB_CONNECTION_POOL_MAX: int = 4
"""Maximum connections in pool."""

DB_CONNECTION_POOL_INCREMENT: int = 1
"""Connections to add when pool exhausted."""

# ─────────────────────────────────────────────────────────────────────────────
#  LLM Timeouts & Behavior
# ─────────────────────────────────────────────────────────────────────────────
LLM_OLLAMA_HEALTH_CHECK_TIMEOUT: int = 2
"""Timeout (seconds) for Ollama health check."""

LLM_OLLAMA_MODELS_TIMEOUT: int = 3
"""Timeout (seconds) for Ollama list models."""

LLM_OLLAMA_GENERATE_TIMEOUT: int = 80
"""Timeout (seconds) for Ollama generate/chat."""

LLM_GEMINI_API_TIMEOUT: int = 60
"""Timeout (seconds) for Gemini API calls."""

LLM_GEMINI_MODELS_TIMEOUT: int = 5
"""Timeout (seconds) for Gemini list models."""

# ─────────────────────────────────────────────────────────────────────────────
#  Gemma4 Model Configuration
# ─────────────────────────────────────────────────────────────────────────────
GEMMA4_TEMPERATURE: float = 1.0
"""Temperature for gemma4:e4b (enables chain-of-thought)."""

GEMMA4_TOP_P: float = 0.95
"""Top-P (nucleus sampling) for gemma4."""

GEMMA4_TOP_K: int = 64
"""Top-K for gemma4."""

# ─────────────────────────────────────────────────────────────────────────────
#  Streamlit UI
# ─────────────────────────────────────────────────────────────────────────────
UI_SIDEBAR_MIN_WIDTH: str = "280px"
"""Minimum width for sidebar."""

UI_CHAT_MAX_WIDTH_PERCENT: int = 74
"""Max width of chat bubbles as percentage."""

UI_CHAT_MAX_WIDTH_MOBILE_PERCENT: int = 88
"""Max width of chat bubbles on mobile."""

# ─────────────────────────────────────────────────────────────────────────────
#  Logging
# ─────────────────────────────────────────────────────────────────────────────
LOG_FORMAT: str = "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s"
"""Log message format."""

LOG_FILE_LEVEL: str = "DEBUG"
"""Log level for file output."""

LOG_CONSOLE_LEVEL: str = "INFO"
"""Log level for console output."""

# ─────────────────────────────────────────────────────────────────────────────
#  Validation
# ─────────────────────────────────────────────────────────────────────────────
VALIDATION_FILE_MAX_BYTES: int = 50 * 1024 * 1024  # 50 MB
"""Maximum file upload size."""

VALIDATION_QUERY_MIN_LENGTH: int = 3
"""Minimum query string length."""

VALIDATION_QUERY_MAX_LENGTH: int = 10000
"""Maximum query string length."""

VALIDATION_USERNAME_MIN_LENGTH: int = 3
"""Minimum username length."""

VALIDATION_PASSWORD_MIN_LENGTH: int = 8
"""Minimum password length."""
