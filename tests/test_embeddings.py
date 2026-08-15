"""Tests for the GeminiEmbeddingProvider."""

import unittest
from unittest.mock import MagicMock, patch

from app.embeddings import GeminiEmbeddingProvider

class TestGeminiEmbeddingProvider(unittest.TestCase):
    def test_init_missing_key(self) -> None:
        with self.assertRaises(ValueError):
            GeminiEmbeddingProvider(api_key="")

    @patch("app.embeddings.genai.Client")
    def test_embed_query(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        
        mock_response = MagicMock()
        mock_embedding = MagicMock()
        mock_embedding.values = [0.1, 0.2, 0.3]
        mock_response.embeddings = [mock_embedding]
        mock_client.models.embed_content.return_value = mock_response

        provider = GeminiEmbeddingProvider(api_key="fake-key", model_name="gemini-embedding-001")
        result = provider.embed_query("hello")

        self.assertEqual(result, [0.1, 0.2, 0.3])
        mock_client.models.embed_content.assert_called_once_with(
            model="gemini-embedding-001",
            contents="hello"
        )

    @patch("app.embeddings.genai.Client")
    def test_embed_documents(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        
        mock_response = MagicMock()
        mock_embedding1 = MagicMock()
        mock_embedding1.values = [0.1, 0.2]
        mock_embedding2 = MagicMock()
        mock_embedding2.values = [0.3, 0.4]
        mock_response.embeddings = [mock_embedding1, mock_embedding2]
        mock_client.models.embed_content.return_value = mock_response

        provider = GeminiEmbeddingProvider(api_key="fake-key", model_name="gemini-embedding-001")
        result = provider.embed_documents(["hello", "world"])

        self.assertEqual(result, [[0.1, 0.2], [0.3, 0.4]])
        mock_client.models.embed_content.assert_called_once_with(
            model="gemini-embedding-001",
            contents=["hello", "world"]
        )

    @patch("app.embeddings.genai.Client")
    def test_embed_documents_empty(self, mock_client_cls: MagicMock) -> None:
        provider = GeminiEmbeddingProvider(api_key="fake-key")
        self.assertEqual(provider.embed_documents([]), [])

if __name__ == "__main__":
    unittest.main()
