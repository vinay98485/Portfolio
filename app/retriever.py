"""Retrieval layer for the Portfolio RAG Assistant.

Accepts a user question, generates an embedding with the configured Gemini Embedding model,
queries the ChromaDB vector store, and returns structured JSON results.

No LLM is called — this module performs retrieval only.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import threading
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import chromadb
from app.embeddings import GeminiEmbeddingProvider

from app.config import config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RetrievedChunk:
    """A single chunk returned from the vector store."""

    rank: int
    chunk_id: str
    text: str
    similarity_score: float          # cosine-like similarity in [0, 1]
    distance: float                  # raw L2 distance from ChromaDB
    metadata: dict[str, Any]
    source: str


@dataclass
class RetrievalResult:
    """Structured response envelope returned by the retriever."""

    found: bool
    query: str
    top_k: int
    score_threshold: float
    total_results: int
    results: list[dict[str, Any]] = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


# ---------------------------------------------------------------------------
# Score helpers
# ---------------------------------------------------------------------------


def l2_to_similarity(distance: float) -> float:
    """Convert L2 distance to a 0-1 similarity score.

    For normalized embeddings, L2² = 2 - 2·cos(θ), so
    cos(θ) = 1 - L2²/2.  We clamp the result to [0, 1].
    """
    similarity = 1.0 - distance / 2.0
    return max(0.0, min(1.0, similarity))


# ---------------------------------------------------------------------------
# Retriever
# ---------------------------------------------------------------------------


class PortfolioRetriever:
    """Stateful retriever backed by ChromaDB and SentenceTransformer."""

    def __init__(
        self,
        chroma_dir: Path | None = None,
        collection_name: str | None = None,
        model_name: str | None = None,
        top_k: int | None = None,
        score_threshold: float | None = None,
    ) -> None:
        self.chroma_dir = chroma_dir or config.chroma_db_dir
        self.collection_name = collection_name or config.collection_name
        self.model_name = model_name or config.embedding_model_name
        self.top_k = top_k if top_k is not None else config.top_k
        self.score_threshold = (
            score_threshold if score_threshold is not None else config.similarity_threshold
        )

        self._client_instance = None
        self._collection_instance = None
        self._model_instance = None

        self._model_lock = threading.Lock()
        self._collection_lock = threading.Lock()

        logger.info("Retriever initialized (lazy loading enabled)")

    @property
    def _collection(self) -> Any:
        if self._collection_instance is None:
            with self._collection_lock:
                if self._collection_instance is None:
                    logger.info("Connecting ChromaDB...")
                    self._client_instance = chromadb.PersistentClient(path=str(self.chroma_dir))
                    self._collection_instance = self._client_instance.get_collection(name=self.collection_name)
                    logger.info("ChromaDB ready")
        return self._collection_instance

    @property
    def _model(self) -> Any:
        if self._model_instance is None:
            with self._model_lock:
                if self._model_instance is None:
                    logger.info("Initializing GeminiEmbeddingProvider...")
                    self._model_instance = GeminiEmbeddingProvider(
                        api_key=config.gemini_api_key,
                        model_name=self.model_name
                    )
                    logger.info("GeminiEmbeddingProvider ready")
        return self._model_instance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def query(
        self,
        question: str,
        top_k: int | None = None,
        score_threshold: float | None = None,
        debug: bool = False,
    ) -> RetrievalResult:
        """Run a semantic query and return structured results."""
        k = top_k if top_k is not None else self.top_k
        threshold = score_threshold if score_threshold is not None else self.score_threshold

        question = question.strip()
        if not question:
            logger.warning("Empty question received")
            return RetrievalResult(
                found=False,
                query=question,
                top_k=k,
                score_threshold=threshold,
                total_results=0,
                message="Empty question provided.",
            )

        logger.info("Query: '%s' | top_k=%d | threshold=%.2f", question, k, threshold)

        # Generate embedding
        embedding = self._model.embed_query(question)

        # Determine filter
        q_lower = question.lower()
        where_filter = None
        if any(kw in q_lower for kw in ["deep learning", "neural network", "cnn", "ann"]):
            where_filter = {"$and": [{"category": "project"}, {"domain": "deep_learning"}]}
        elif "churn" in q_lower:
            where_filter = {"category": "project"}
        elif any(kw in q_lower for kw in ["machine learning", "algorithm", "prediction"]):
            where_filter = {"$and": [{"category": "project"}, {"domain": "machine_learning"}]}
        elif any(kw in q_lower for kw in ["skills", "technologies", "tools"]):
            where_filter = {"category": "skills"}
        elif any(kw in q_lower for kw in ["education", "degree"]):
            where_filter = {"category": "education"}
        elif any(kw in q_lower for kw in ["project", "built", "developed", "created", "application"]):
            where_filter = {"category": "project"}

        def execute_query(filter_dict: dict[str, str] | None) -> list[dict[str, Any]]:
            kwargs: dict[str, Any] = {
                "query_embeddings": embedding,
                "n_results": k,
                "include": ["documents", "metadatas", "distances"],
            }
            if filter_dict:
                kwargs["where"] = filter_dict
                
            raw = self._collection.query(**kwargs)

            ids = raw.get("ids", [[]])[0]
            documents = raw.get("documents", [[]])[0]
            metadatas = raw.get("metadatas", [[]])[0]
            distances = raw.get("distances", [[]])[0]

            res: list[dict[str, Any]] = []
            for rank, (chunk_id, text, meta, dist) in enumerate(
                zip(ids, documents, metadatas, distances), start=1
            ):
                if dist > threshold:
                    logger.debug(
                        "Skipping chunk %s (distance=%.4f > threshold=%.2f)",
                        chunk_id,
                        dist,
                        threshold,
                    )
                    continue

                similarity = round(l2_to_similarity(dist), 4)
                chunk = RetrievedChunk(
                    rank=rank,
                    chunk_id=chunk_id,
                    text=text,
                    similarity_score=similarity,
                    distance=round(dist, 4),
                    metadata=meta,
                    source=meta.get("source", "unknown"),
                )
                res.append(asdict(chunk))
            return res

        results = execute_query(where_filter)

        if not results and where_filter:
            logger.info("Filtered query returned no results, falling back to unrestricted search")
            results = execute_query(None)

        if debug:
            print("\n" + "=" * 70)
            print(f"[DEBUG RETRIEVER] Query: '{question}'")
            print(f"[DEBUG RETRIEVER] Filter Applied: {where_filter}")
            print(f"[DEBUG RETRIEVER] Total Chunks Retrieved: {len(results)}")
            print("=" * 70)
            for item in results:
                preview = item["text"].replace("\n", " ").strip()
                if len(preview) > 150:
                    preview = preview[:150] + "..."
                print(f"Rank #{item['rank']}")
                print(f"  Source           : {item['source']}")
                print(f"  Metadata         : {item['metadata']}")
                print(f"  Similarity Score : {item['similarity_score']} (Distance: {item['distance']})")
                print(f"  Chunk Preview    : {preview}")
                print("-" * 70)
            print("=" * 70 + "\n")

        if not results:
            logger.info("No results above threshold for query: '%s'", question)
            return RetrievalResult(
                found=False,
                query=question,
                top_k=k,
                score_threshold=threshold,
                total_results=0,
                message="Information not found in portfolio.",
            )

        logger.info(
            "Returning %d result(s) for query: '%s'",
            len(results),
            question,
        )
        return RetrievalResult(
            found=True,
            query=question,
            top_k=k,
            score_threshold=threshold,
            total_results=len(results),
            results=results,
        )

    def get_collection_stats(self) -> dict[str, Any]:
        """Return basic stats about the underlying collection."""
        count = self._collection.count()
        meta = self._collection.metadata or {}
        return {
            "collection_name": self.collection_name,
            "vector_count": count,
            "embedding_model": meta.get("embedding_model", self.model_name),
            "chroma_dir": str(self.chroma_dir),
        }
