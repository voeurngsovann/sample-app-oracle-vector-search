"""
config.py - Centralized configuration management

All environment variables, database settings, and configuration logic
consolidated in one place for easy maintenance and validation.
"""
from __future__ import annotations

import os
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Application-wide configuration from environment variables."""
    
    # ─── Oracle Database Settings ───────────────────────────────────────────
    ora_user: str = os.environ.get("ORA_USER", "")
    ora_password: str = os.environ.get("ORA_PASSWORD", "")
    ora_host: str = os.environ.get("ORA_HOST", "localhost")
    ora_port: int = int(os.environ.get("ORA_PORT", 1521))
    ora_service: str = os.environ.get("ORA_SERVICE", "")
    ora_schema: str = os.environ.get("ORA_SCHEMA", "DEV").upper()
    
    # ─── Table Names ────────────────────────────────────────────────────────
    ora_doc_table: str = os.environ.get("ORA_DOC_TABLE", "AITEST_DOCUMENTATION_TAB").upper()
    ora_chunk_table: str = os.environ.get("ORA_CHUNK_TABLE", "AITEST_DOCUMENTATION_CHUNKS").upper()
    
    # ─── ONNX Model Settings ────────────────────────────────────────────────
    ora_onnx_model: str = os.environ.get("ORA_ONNX_MODEL", "ALL_MINILM_L12_V2").upper()
    
    # ─── Vector Search Settings ─────────────────────────────────────────────
    vector_top_k: int = int(os.environ.get("VECTOR_TOP_K", 5))
    vector_distance: str = os.environ.get("VECTOR_DISTANCE", "COSINE").upper()
    
    # ─── LLM Provider Settings ──────────────────────────────────────────────
    llm_provider: str = os.environ.get("LLM_PROVIDER", "ollama").lower().strip()
    
    # Ollama
    ollama_base_url: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/api").rstrip("/")
    ollama_model: str = os.environ.get("OLLAMA_MODEL", "gemma4:e4b")
    
    # Gemini
    gemini_api_key: str = os.environ.get("GEMINI_API_KEY", "")
    gemini_model: str = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")
    gemini_temperature: float = float(os.environ.get("GEMINI_TEMPERATURE", "0.7"))
    gemini_max_tokens: int = int(os.environ.get("GEMINI_MAX_TOKENS", "1024"))
    
    # ─── Streamlit Settings ─────────────────────────────────────────────────
    streamlit_page_title: str = "VectorSearch · Oracle 26ai"
    streamlit_page_icon: str = "◈"
    
    # ─── Auth Settings ──────────────────────────────────────────────────────
    auth_pbkdf2_iterations: int = 260_000  # OWASP 2024 recommendation
    auth_session_timeout_minutes: int = int(os.environ.get("AUTH_SESSION_TIMEOUT", "30"))
    
    @property
    def ora_dsn(self) -> str:
        """Oracle connection string."""
        return f"{self.ora_host}:{self.ora_port}/{self.ora_service}"
    
    @property
    def ora_fq_doc_table(self) -> str:
        """Fully qualified document table name."""
        return f"{self.ora_schema}.{self.ora_doc_table}"
    
    @property
    def ora_fq_chunk_table(self) -> str:
        """Fully qualified chunk table name."""
        return f"{self.ora_schema}.{self.ora_chunk_table}"
    
    @property
    def ora_fq_onnx_model(self) -> str:
        """Fully qualified ONNX model name."""
        return f"{self.ora_schema}.{self.ora_onnx_model}"
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate critical configuration values.
        Returns (is_valid, list_of_errors).
        """
        errors = []
        
        # Critical database settings
        if not self.ora_user:
            errors.append("ORA_USER environment variable not set")
        if not self.ora_password:
            errors.append("ORA_PASSWORD environment variable not set")
        if not self.ora_service:
            errors.append("ORA_SERVICE environment variable not set")
        
        # Vector search settings
        if self.vector_top_k <= 0:
            errors.append(f"VECTOR_TOP_K must be > 0, got {self.vector_top_k}")
        
        # LLM settings
        if self.llm_provider == "gemini" and not self.gemini_api_key:
            errors.append("GEMINI_API_KEY required when LLM_PROVIDER=gemini")
        
        return len(errors) == 0, errors


# ─────────────────────────────────────────────────────────────────────────────
#  Global config instance
# ─────────────────────────────────────────────────────────────────────────────
config = AppConfig()

# Validate on import
is_valid, errors = config.validate()
if not is_valid:
    logger.error("Configuration validation failed:")
    for error in errors:
        logger.error(f"  - {error}")
