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
    # NOTE: llm_provider is intentionally NOT a dataclass field — it must be
    # read dynamically from os.environ so runtime switches from the UI take
    # effect immediately. All other LLM settings are fixed at startup.

    # Ollama
    ollama_base_url: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/api").rstrip("/")
    ollama_model: str = os.environ.get("OLLAMA_MODEL", "gemma4:e4b")

    # Gemini
    gemini_api_key: str = os.environ.get("GEMINI_API_KEY", "")
    gemini_model: str = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")
    gemini_temperature: float = float(os.environ.get("GEMINI_TEMPERATURE", "0.7"))
    gemini_max_tokens: int = int(os.environ.get("GEMINI_MAX_TOKENS", "1024"))

    @property
    def llm_provider(self) -> str:
        """Read LLM_PROVIDER from env on every call so UI switches take effect instantly."""
        return os.environ.get("LLM_PROVIDER", "ollama").lower().strip()
    
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
    
    @property
    def ora_pk_chunk(self) -> str:
        """Primary key constraint name for chunk table."""
        return f"PK_{self.ora_chunk_table[:20]}"
    
    @property
    def ora_fk_chunk_doc(self) -> str:
        """Foreign key constraint name for chunk->doc relationship."""
        return f"FK_{self.ora_chunk_table[:15]}_DOC"

    # Backwards-compatible aliases for existing code that expects `cfg` names
    @property
    def user(self) -> str:
        return self.ora_user

    @property
    def password(self) -> str:
        return self.ora_password

    @property
    def host(self) -> str:
        return self.ora_host

    @property
    def port(self) -> int:
        return self.ora_port

    @property
    def service(self) -> str:
        return self.ora_service

    @property
    def schema(self) -> str:
        return self.ora_schema

    @property
    def doc_table(self) -> str:
        return self.ora_doc_table

    @property
    def chunk_table(self) -> str:
        return self.ora_chunk_table

    @property
    def onnx_model(self) -> str:
        return self.ora_onnx_model

    @property
    def fq_doc_table(self) -> str:
        return self.ora_fq_doc_table

    @property
    def fq_chunk_table(self) -> str:
        return self.ora_fq_chunk_table

    @property
    def fq_onnx_model(self) -> str:
        return self.ora_fq_onnx_model

    @property
    def pk_chunk(self) -> str:
        return self.ora_pk_chunk

    @property
    def fk_chunk_doc(self) -> str:
        return self.ora_fk_chunk_doc

    @property
    def dsn(self) -> str:
        return self.ora_dsn

    @property
    def top_k(self) -> int:
        return self.vector_top_k

    @property
    def distance(self) -> str:
        return self.vector_distance
    
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
        
        # LLM settings — only warn, never block startup
        # Both providers can be configured simultaneously; the active one
        # is chosen at runtime via the UI, not at startup.
        if self.gemini_api_key and not self.gemini_model:
            errors.append("GEMINI_MODEL must be set when GEMINI_API_KEY is provided")
        
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
