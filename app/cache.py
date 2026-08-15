"""Answer cache for the Portfolio RAG Assistant.

Caches question→answer pairs on disk as JSON with configurable TTL.
Reduces redundant Gemini API calls for repeated or similar questions.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import config
from app.generator import is_valid_cached_answer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Key normalisation
# ---------------------------------------------------------------------------


def normalize_question(question: str) -> str:
    """Produce a stable cache key from a question string."""
    text = question.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = text.rstrip("?!.")
    return text


def cache_key(question: str) -> str:
    """Return a hex digest suitable as a dict key."""
    normalised = normalize_question(question)
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()[:24]


# ---------------------------------------------------------------------------
# Cache entry
# ---------------------------------------------------------------------------


def _now() -> float:
    return time.time()


def _iso_now() -> str:
    """Return current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# AnswerCache
# ---------------------------------------------------------------------------


class AnswerCache:
    """File-backed TTL answer cache."""

    def __init__(
        self,
        cache_path: Path | None = None,
        ttl_hours: int | None = None,
        enabled: bool | None = None,
    ) -> None:
        self.cache_path = cache_path or config.cache_path
        self.ttl_seconds = (ttl_hours if ttl_hours is not None else config.cache_ttl_hours) * 3600
        self.enabled = enabled if enabled is not None else config.cache_enabled
        self._store: dict[str, dict[str, Any]] = {}

        if self.enabled:
            self._load()
            logger.info(
                "Answer cache initialised — %d entries, TTL=%dh, path=%s",
                len(self._store),
                self.ttl_seconds // 3600,
                self.cache_path,
            )
        else:
            logger.info("Answer cache disabled")

    def _load(self) -> None:
        if not self.cache_path.exists():
            self._store = {}
            return
        try:
            raw = self.cache_path.read_text(encoding="utf-8")
            self._store = json.loads(raw) if raw.strip() else {}
            logger.debug("Loaded %d cache entries from disk", len(self._store))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read cache file, starting fresh: %s", exc)
            self._store = {}

    def _save(self) -> None:
        try:
            self.cache_path.write_text(
                json.dumps(self._store, indent=2, default=str),
                encoding="utf-8",
            )
        except OSError as exc:
            logger.error("Failed to write cache file: %s", exc)

    def get(self, question: str) -> dict[str, Any] | None:
        """Look up a cached answer."""
        if not self.enabled:
            return None

        key = cache_key(question)
        entry = self._store.get(key)

        if entry is None:
            logger.info("CACHE_MISS key=%s question='%s'", key, question)
            return None

        age = _now() - entry.get("timestamp", 0)
        if age > self.ttl_seconds:
            logger.info(
                "CACHE_MISS (expired) key=%s (age=%.0fs > ttl=%ds)",
                key,
                age,
                self.ttl_seconds,
            )
            del self._store[key]
            self._save()
            return None

        cached_answer = entry.get("answer", "")
        if not is_valid_cached_answer(cached_answer):
            logger.warning(
                "CACHE_SKIPPED key=%s — evicting poisoned entry (answer starts with: '%.60s…')",
                key,
                cached_answer,
            )
            del self._store[key]
            self._save()
            return None

        logger.info("CACHE_HIT key=%s question='%s'", key, question)
        return {
            "answer": cached_answer,
            "sources": entry["sources"],
            "cached": True,
            "cache_age_seconds": round(age),
        }

    def put(
        self,
        question: str,
        answer: str,
        sources: list[str],
    ) -> None:
        """Store an answer in the cache."""
        if not self.enabled:
            return

        key = cache_key(question)
        self._store[key] = {
            "question_hash": key,
            "answer": answer,
            "sources": sources,
            "created_at": _iso_now(),
            "timestamp": _now(),
            "question": normalize_question(question),
        }
        self._save()
        logger.info(
            "CACHE_STORED key=%s question='%s' sources=%s",
            key,
            question,
            sources,
        )

    def clear(self) -> int:
        """Remove all entries."""
        count = len(self._store)
        self._store = {}
        self._save()
        logger.info("CACHE_CLEARED — removed %d entries", count)
        return count

    def purge_expired(self) -> int:
        """Remove only expired entries."""
        now = _now()
        expired_keys = [
            k
            for k, v in self._store.items()
            if now - v.get("timestamp", 0) > self.ttl_seconds
        ]
        for k in expired_keys:
            del self._store[k]
        if expired_keys:
            self._save()
        logger.info("Purged %d expired cache entries", len(expired_keys))
        return len(expired_keys)

    def stats(self) -> dict[str, Any]:
        """Return cache statistics."""
        now = _now()
        active = sum(
            1
            for v in self._store.values()
            if now - v.get("timestamp", 0) <= self.ttl_seconds
        )
        return {
            "enabled": self.enabled,
            "total_entries": len(self._store),
            "active_entries": active,
            "expired_entries": len(self._store) - active,
            "ttl_hours": self.ttl_seconds // 3600,
            "cache_path": str(self.cache_path),
        }
