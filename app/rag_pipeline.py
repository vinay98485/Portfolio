"""RAG Pipeline service layer for Portfolio RAG Assistant.

Flow:
    Question → Retriever → Cache Check → Generator → Cache Store → Return Response

Exposes:
    - ask_question(question, use_cache=True) -> dict
    - RAGPipeline class
"""

from __future__ import annotations

import gc
import logging
import os
import time
import threading
from typing import Any

try:
    import psutil
    def get_memory_mb() -> float:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
except ImportError:
    def get_memory_mb() -> float:
        return 0.0

from app.cache import AnswerCache
from app.config import config
from app.generator import GenerationResult, PortfolioGenerator, is_cacheable
from app.retriever import PortfolioRetriever

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Application service orchestrating retrieval, caching, and generation."""

    def __init__(
        self,
        retriever: PortfolioRetriever | None = None,
        generator: PortfolioGenerator | None = None,
        cache: AnswerCache | None = None,
    ) -> None:
        logger.info("Initializing RAGPipeline...")
        self.retriever = retriever or PortfolioRetriever(
            top_k=config.top_k,
            score_threshold=config.similarity_threshold,
        )
        self.generator = generator or PortfolioGenerator()
        self.cache = cache or AnswerCache(
            ttl_hours=config.cache_ttl_hours,
            enabled=config.cache_enabled,
        )
        logger.info("RAGPipeline ready (Memory: %.2f MB)", get_memory_mb())

    def ask_question(self, question: str, use_cache: bool = True, debug: bool = False) -> dict[str, Any]:
        """Execute the RAG pipeline flow for a user question."""
        start_total = time.time()
        question = (question or "").strip()
        if not question:
            return {
                "answer": "Please provide a question.",
                "sources": [],
                "cached": False,
            }

        logger.info("START pipeline question='%s' | Memory: %.2f MB", question[:80], get_memory_mb())

        # Step 1: Cache Check
        if use_cache and self.cache.enabled:
            cached_result = self.cache.get(question)
            if cached_result is not None:
                total_ms = int(round((time.time() - start_total) * 1000))
                logger.info("CACHE_HIT for pipeline query")
                logger.info("TOTAL_TIME: %dms (cached)", total_ms)
                return {
                    "answer": cached_result["answer"],
                    "sources": cached_result["sources"],
                    "cached": True,
                }

        # Step 2: Retrieve
        logger.info("BEFORE_RETRIEVAL Memory: %.2f MB", get_memory_mb())
        start_retrieval = time.time()
        logger.info("Retrieving context from vector store...")
        retrieval = self.retriever.query(question, debug=debug)
        retrieval_ms = int(round((time.time() - start_retrieval) * 1000))
        logger.info("RETRIEVAL_TIME: %dms", retrieval_ms)
        logger.info("AFTER_RETRIEVAL Memory: %.2f MB", get_memory_mb())

        # Step 3: Generator
        start_generation = time.time()
        result: GenerationResult = self.generator.generate(
            question=question,
            retrieval_results=retrieval.results,
            retrieval_found=retrieval.found,
        )
        generation_ms = int(round((time.time() - start_generation) * 1000))
        logger.info("GENERATION_TIME: %dms", generation_ms)
        logger.info("AFTER_GENERATION Memory: %.2f MB", get_memory_mb())

        # Step 4: Cache Store
        if use_cache and self.cache.enabled:
            if is_cacheable(result):
                self.cache.put(
                    question=question,
                    answer=result.answer,
                    sources=result.sources,
                )
            else:
                logger.warning("CACHE_SKIPPED for uncacheable generation result")

        total_ms = int(round((time.time() - start_total) * 1000))
        logger.info("TOTAL_TIME: %dms", total_ms)

        # Step 5: Clean up memory
        gc.collect()
        logger.info("AFTER_GC Memory: %.2f MB", get_memory_mb())

        # Step 6: Return Response
        return {
            "answer": result.answer,
            "sources": result.sources,
            "cached": False,
        }


# Global singleton instance for module-level ask_question interface
_pipeline_lock = threading.Lock()
_default_pipeline: RAGPipeline | None = None


def get_pipeline() -> RAGPipeline:
    """Get or create the global default RAGPipeline instance."""
    global _default_pipeline
    if _default_pipeline is None:
        with _pipeline_lock:
            if _default_pipeline is None:
                _default_pipeline = RAGPipeline()
    return _default_pipeline


def ask_question(question: str, use_cache: bool = True, debug: bool = False) -> dict[str, Any]:
    pipeline = get_pipeline()
    return pipeline.ask_question(question, use_cache=use_cache, debug=debug)
