"""Generation layer for the Portfolio RAG Assistant.

Builds structured context from retrieved chunks and sends it to
Gemini with a strict hallucination-preventing system prompt.

Features:
  - Exponential-backoff retry for transient Gemini errors (429/5xx)
  - is_cacheable() gate to prevent caching failures
  - Structured logging: GENERATION_STARTED, GEMINI_REQUEST, GEMINI_SUCCESS,
    GEMINI_RETRY, GEMINI_FAILURE

This module never calls Gemini when retrieval returns no results.
"""

from __future__ import annotations

import json
import logging
import time
import threading
from dataclasses import asdict, dataclass, field
from typing import Any

from google import genai
from google.genai import types

from app.config import config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt — strict anti-hallucination rules
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are Vinay AI.

You answer questions about Vinay Kumar Mandalapu.

Rules:
- Only use retrieved context.
- Never invent information.
- Never invent projects.
- Never invent skills.
- Never invent achievements.
- If information is missing, respond:
  "I couldn't find that information in Vinay's portfolio."
- Be concise, professional, and recruiter-friendly.
- When listing projects, skills, or achievements, use bullet points.
- Always cite which source document the information came from when possible.
"""

FALLBACK_ANSWER = "I couldn't find that information in Vinay's portfolio."
TEMPORARILY_UNAVAILABLE = (
    "The AI service is temporarily unavailable. Please try again later."
)

# HTTP status codes that justify a retry (transient errors only)
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

# Retry schedule: (attempt_number, wait_seconds)
RETRY_DELAYS = [1, 2, 4]  # 3 retries with exponential backoff
MAX_ATTEMPTS = len(RETRY_DELAYS) + 1  # initial attempt + retries


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class GenerationResult:
    """Structured response from the generation layer."""

    answer: str
    sources: list[str]
    question: str = ""
    cached: bool = False
    retrieval_found: bool = True
    chunks_used: int = 0
    model: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


# ---------------------------------------------------------------------------
# Cacheability check
# ---------------------------------------------------------------------------


def is_cacheable(result: GenerationResult) -> bool:
    """Return True only if the result represents a successful generation."""
    if not result.retrieval_found:
        return False
    if not result.answer or not result.answer.strip():
        return False
    if result.answer == TEMPORARILY_UNAVAILABLE:
        return False
    if result.answer == FALLBACK_ANSWER:
        return False
    return True


def is_valid_cached_answer(answer: str) -> bool:
    """Check if a cached answer string is still valid."""
    if not answer or not answer.strip():
        return False
    if answer == TEMPORARILY_UNAVAILABLE:
        return False
    if answer.startswith("Sorry, I encountered an error"):
        return False
    return True


# ---------------------------------------------------------------------------
# Retry helpers
# ---------------------------------------------------------------------------


def _extract_status_code(exc: Exception) -> int | None:
    """Extract HTTP status code from an exception."""
    if hasattr(exc, "status_code"):
        return exc.status_code
    if hasattr(exc, "__cause__") and hasattr(exc.__cause__, "status_code"):
        return exc.__cause__.status_code
    return None


def _is_retryable(exc: Exception) -> bool:
    """Return True if the exception represents a transient failure."""
    code = _extract_status_code(exc)
    if code is not None and code in RETRYABLE_STATUS_CODES:
        return True
    exc_str = str(exc)
    for status in RETRYABLE_STATUS_CODES:
        if str(status) in exc_str:
            return True
    return False


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------


def build_context(
    results: list[dict[str, Any]],
    max_chunks: int | None = None,
) -> str:
    """Build a numbered context block from retrieved chunks."""
    limit = max_chunks or config.max_context_chunks
    selected = results[:limit]

    if not selected:
        return ""

    sections: list[str] = []
    for i, chunk in enumerate(selected, start=1):
        meta = chunk.get("metadata", {})
        source = chunk.get("source", meta.get("source", "unknown"))
        title = meta.get("title", "")
        category = meta.get("category", "")
        project = meta.get("project_name", "")
        sim = chunk.get("similarity_score", 0)

        header_parts = [f"[Source {i}: {source}]"]
        if title:
            header_parts.append(f"Title: {title}")
        if project:
            header_parts.append(f"Project: {project}")
        if category:
            header_parts.append(f"Category: {category}")
        header_parts.append(f"Relevance: {sim:.2%}")

        header = "\n".join(header_parts)
        text = chunk.get("text", "")
        sections.append(f"{header}\n\n{text}")

    context = "\n\n---\n\n".join(sections)

    logger.info(
        "Built context from %d chunk(s), total length=%d chars",
        len(selected),
        len(context),
    )
    return context


def extract_sources(results: list[dict[str, Any]]) -> list[str]:
    """Deduplicate source file paths from results."""
    seen: set[str] = set()
    sources: list[str] = []
    for chunk in results:
        src = chunk.get("source", chunk.get("metadata", {}).get("source", ""))
        if src and src not in seen:
            seen.add(src)
            sources.append(src)
    return sources


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------


class PortfolioGenerator:
    """Generates answers using Gemini with retrieved context."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        max_context_chunks: int | None = None,
    ) -> None:
        self.api_key = api_key or config.gemini_api_key
        self.model_name = model_name or config.gemini_model
        self.max_output_tokens = max_output_tokens or config.max_output_tokens
        self.temperature = temperature if temperature is not None else config.temperature
        self.max_context_chunks = max_context_chunks or config.max_context_chunks

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Add it to .env or pass api_key=."
            )

        self._client_instance = None
        self._client_lock = threading.Lock()
        logger.info("Generator initialized (lazy loading enabled)")

    @property
    def _client(self) -> Any:
        if self._client_instance is None:
            with self._client_lock:
                if self._client_instance is None:
                    self._client_instance = genai.Client(api_key=self.api_key)
                    logger.info("Gemini client initialized (%s)", self.model_name)
        return self._client_instance

    def _call_gemini(self, user_prompt: str) -> str:
        """Call Gemini API with exponential-backoff retry."""
        last_exc: Exception | None = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                logger.info(
                    "GEMINI_REQUEST attempt=%d/%d model=%s prompt_length=%d",
                    attempt,
                    MAX_ATTEMPTS,
                    self.model_name,
                    len(user_prompt),
                )

                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        max_output_tokens=self.max_output_tokens,
                        temperature=self.temperature,
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                    ),
                )

                raw_text = response.text
                answer = raw_text.strip() if raw_text else ""
                if not answer:
                    for part in (response.candidates or [{}])[0].content.parts:
                        if hasattr(part, "text") and part.text:
                            answer = part.text.strip()
                            break

                logger.info(
                    "GEMINI_SUCCESS attempt=%d answer_length=%d",
                    attempt,
                    len(answer),
                )
                return answer

            except Exception as exc:
                last_exc = exc
                status = _extract_status_code(exc) or "unknown"

                if not _is_retryable(exc):
                    logger.error(
                        "GEMINI_FAILURE attempt=%d status=%s non-retryable — %s",
                        attempt,
                        status,
                        exc,
                    )
                    raise

                if attempt < MAX_ATTEMPTS:
                    delay = RETRY_DELAYS[attempt - 1]
                    logger.warning(
                        "GEMINI_RETRY attempt=%d/%d status=%s waiting=%ds — %s",
                        attempt,
                        MAX_ATTEMPTS,
                        status,
                        delay,
                        exc,
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        "GEMINI_FAILURE all %d attempts exhausted status=%s — %s",
                        MAX_ATTEMPTS,
                        status,
                        exc,
                    )

        raise last_exc  # type: ignore[misc]

    def generate(
        self,
        question: str,
        retrieval_results: list[dict[str, Any]],
        retrieval_found: bool = True,
    ) -> GenerationResult:
        """Generate an answer from retrieval results."""
        question = question.strip()
        sources = extract_sources(retrieval_results)

        logger.info("GENERATION_STARTED question='%s'", question[:80])

        if not retrieval_found or not retrieval_results:
            logger.info(
                "Retrieval returned no results — returning fallback (Gemini NOT called)"
            )
            return GenerationResult(
                answer=FALLBACK_ANSWER,
                sources=[],
                question=question,
                cached=False,
                retrieval_found=False,
                chunks_used=0,
                model=self.model_name,
            )

        context = build_context(
            retrieval_results,
            max_chunks=self.max_context_chunks,
        )
        chunks_used = min(len(retrieval_results), self.max_context_chunks)

        user_prompt = (
            f"Context:\n\n{context}\n\n---\n\n"
            f"Question: {question}\n\n"
            f"Answer based ONLY on the context above. Be concise and limit your answer to a maximum of 200 words."
        )

        try:
            answer = self._call_gemini(user_prompt)

            if not answer:
                answer = FALLBACK_ANSWER
                logger.warning("Gemini returned empty response — using fallback")

        except Exception as exc:
            logger.error(
                "GEMINI_FAILURE — returning temporary-unavailable response: %s",
                exc,
            )
            return GenerationResult(
                answer=TEMPORARILY_UNAVAILABLE,
                sources=sources,
                question=question,
                cached=False,
                retrieval_found=True,
                chunks_used=chunks_used,
                model=self.model_name,
            )

        return GenerationResult(
            answer=answer,
            sources=sources,
            question=question,
            cached=False,
            retrieval_found=True,
            chunks_used=chunks_used,
            model=self.model_name,
        )
