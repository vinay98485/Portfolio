"""Embedding provider utilizing the Google Gemini API.

Replaces local sentence-transformers models to reduce RAM consumption.
"""

from __future__ import annotations

import logging
from typing import Any

from google import genai

logger = logging.getLogger(__name__)


class GeminiEmbeddingProvider:
    """Provides embedding generation using the Gemini Embedding API."""

    def __init__(self, api_key: str, model_name: str = "gemini-embedding-001") -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for Gemini embeddings.")
        self.api_key = api_key
        self.model_name = model_name
        self._client = genai.Client(api_key=self.api_key)
        logger.info("GeminiEmbeddingProvider initialized with model: %s", self.model_name)

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query string.
        
        Returns:
            list[float]: The embedding vector.
        """
        response = self._client.models.embed_content(
            model=self.model_name,
            contents=text,
        )
        # response.embeddings is a list of Embedding objects, we extract the first one
        return response.embeddings[0].values

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of document strings.
        
        Returns:
            list[list[float]]: The list of embedding vectors.
        """
        if not texts:
            return []

        response = self._client.models.embed_content(
            model=self.model_name,
            contents=texts,
        )
        return [emb.values for emb in response.embeddings]
