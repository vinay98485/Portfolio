"""Centralized configuration module for Portfolio RAG Assistant.

Manages and validates all environment variables and configuration settings:
- Required: GEMINI_API_KEY
- Defaults:
  - GEMINI_EMBEDDING_MODEL ("gemini-embedding-001")
  - CHROMA_DB_PATH ("database/chroma_db")
  - TOP_K (3)
  - SCORE_THRESHOLD (1.6)
  - CACHE_ENABLED (true)
  - CACHE_TTL_HOURS (168)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


class ConfigurationError(ValueError):
    """Raised when required configuration is missing or invalid."""

    pass


@dataclass(frozen=True)
class Config:
    """Centralised configuration loaded from environment variables."""

    # Project Paths
    root_dir: Path = field(default_factory=lambda: ROOT_DIR)
    knowledge_dir: Path = field(default_factory=lambda: ROOT_DIR / "knowledge")
    chroma_db_path: Path = field(default_factory=lambda: ROOT_DIR / "database" / "chroma_db")
    cache_path: Path = field(default_factory=lambda: ROOT_DIR / "answer_cache.json")

    # Vector Store & Embedding Model
    collection_name: str = "portfolio_knowledge"
    gemini_embedding_model: str = "gemini-embedding-001"

    # Gemini LLM Settings
    gemini_api_key: str = field(repr=False, default="")
    gemini_model: str = "gemini-3.1-flash-lite"
    max_output_tokens: int = 1024
    temperature: float = 0.2

    # Retrieval Settings
    top_k: int = 3
    score_threshold: float = 1.6
    max_context_chunks: int = 5

    # Cache Settings
    cache_enabled: bool = True
    cache_ttl_hours: int = 168          # 7 days

    # Logging Settings
    log_level: str = "INFO"

    # Backward compatibility properties
    @property
    def chroma_db_dir(self) -> Path:
        return self.chroma_db_path

    @property
    def embedding_model_name(self) -> str:
        return self.gemini_embedding_model

    @property
    def similarity_threshold(self) -> float:
        return self.score_threshold


def _bool(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "on")


def load_config(validate: bool = True, env: dict[str, str] | None = None) -> Config:
    """Build a Config instance from environment variables with defaults and validation.

    Parameters
    ----------
    validate:
        Whether to enforce validation of required variables (such as GEMINI_API_KEY).
    env:
        Optional dictionary to read env vars from (defaults to os.environ).

    Raises
    ------
    ConfigurationError:
        If required configuration is missing or invalid.
    """
    get_env = env.get if env is not None else os.getenv

    api_key = (get_env("GEMINI_API_KEY") or "").strip()

    if validate and not api_key:
        raise ConfigurationError(
            "Missing required environment variable: GEMINI_API_KEY. "
            "Please set GEMINI_API_KEY in your .env file or environment variables."
        )

    # Embedding model name
    emb_model = get_env("GEMINI_EMBEDDING_MODEL") or get_env(
        "EMBEDDING_MODEL_NAME", "gemini-embedding-001"
    )

    # ChromaDB path
    chroma_path_str = get_env("CHROMA_DB_PATH") or get_env("CHROMA_DB_DIR", "database/chroma_db")
    chroma_path = Path(chroma_path_str)
    if not chroma_path.is_absolute():
        chroma_path = ROOT_DIR / chroma_path

    # Knowledge directory
    k_dir_str = get_env("KNOWLEDGE_DIR", "knowledge")
    k_dir = Path(k_dir_str)
    if not k_dir.is_absolute():
        k_dir = ROOT_DIR / k_dir

    # Top K
    top_k_str = get_env("TOP_K", "3")
    try:
        top_k = int(top_k_str)
    except ValueError:
        raise ConfigurationError(f"Invalid integer for TOP_K: '{top_k_str}'")

    # Score / similarity threshold
    thresh_str = get_env("SCORE_THRESHOLD") or get_env("SIMILARITY_THRESHOLD", "1.6")
    try:
        score_threshold = float(thresh_str)
    except ValueError:
        raise ConfigurationError(f"Invalid float for SCORE_THRESHOLD: '{thresh_str}'")

    # Cache enabled
    cache_enabled_str = get_env("CACHE_ENABLED", "true")
    cache_enabled = _bool(cache_enabled_str)

    # Cache TTL hours
    ttl_str = get_env("CACHE_TTL_HOURS", "168")
    try:
        cache_ttl_hours = int(ttl_str)
    except ValueError:
        raise ConfigurationError(f"Invalid integer for CACHE_TTL_HOURS: '{ttl_str}'")

    return Config(
        gemini_api_key=api_key,
        gemini_model=get_env("GEMINI_MODEL", "gemini-3.1-flash-lite"),
        gemini_embedding_model=emb_model,
        chroma_db_path=chroma_path,
        knowledge_dir=k_dir,
        top_k=top_k,
        score_threshold=score_threshold,
        max_context_chunks=int(get_env("MAX_CONTEXT_CHUNKS", "5")),
        max_output_tokens=int(get_env("MAX_OUTPUT_TOKENS", "1024")),
        temperature=float(get_env("TEMPERATURE", "0.2")),
        cache_enabled=cache_enabled,
        cache_ttl_hours=cache_ttl_hours,
        log_level=get_env("LOG_LEVEL", "INFO"),
    )


# Centralized singleton instance
try:
    config = load_config(validate=True)
except ConfigurationError:
    config = load_config(validate=False)
