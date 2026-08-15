"""Unit test suite for app/rag_pipeline.py."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from app.generator import GenerationResult
from app.rag_pipeline import RAGPipeline, ask_question


class TestRAGPipeline(unittest.TestCase):
    """Test suite for RAGPipeline service layer and ask_question interface."""

    def setUp(self) -> None:
        self.mock_retriever = MagicMock()
        self.mock_generator = MagicMock()
        self.mock_cache = MagicMock()

        self.mock_retrieval_res = MagicMock()
        self.mock_retrieval_res.found = True
        self.mock_retrieval_res.results = [
            {"source": "about_me.md", "text": "Vinay is an AI engineer."}
        ]
        self.mock_retriever.query.return_value = self.mock_retrieval_res

        self.mock_gen_result = GenerationResult(
            answer="Vinay is an AI engineer.",
            sources=["about_me.md"],
            question="Tell me about Vinay",
            cached=False,
            retrieval_found=True,
            chunks_used=1,
            model="gemini-3.7-flash",
        )
        self.mock_generator.generate.return_value = self.mock_gen_result

        self.mock_cache.enabled = True
        self.mock_cache.get.return_value = None

        self.pipeline = RAGPipeline(
            retriever=self.mock_retriever,
            generator=self.mock_generator,
            cache=self.mock_cache,
        )

    def test_ask_question_flow(self) -> None:
        res = self.pipeline.ask_question("Tell me about Vinay")

        self.assertEqual(res["answer"], "Vinay is an AI engineer.")
        self.assertEqual(res["sources"], ["about_me.md"])
        self.assertFalse(res["cached"])

        self.mock_cache.get.assert_called_once_with("Tell me about Vinay")
        self.mock_retriever.query.assert_called_once_with("Tell me about Vinay", debug=False)
        self.mock_generator.generate.assert_called_once()
        self.mock_cache.put.assert_called_once_with(
            question="Tell me about Vinay",
            answer="Vinay is an AI engineer.",
            sources=["about_me.md"],
        )

    def test_ask_question_cache_hit(self) -> None:
        self.mock_cache.get.return_value = {
            "answer": "Cached answer about Vinay",
            "sources": ["about_me.md"],
            "cached": True,
        }

        res = self.pipeline.ask_question("Tell me about Vinay")

        self.assertEqual(res["answer"], "Cached answer about Vinay")
        self.assertEqual(res["sources"], ["about_me.md"])
        self.assertTrue(res["cached"])

        self.mock_cache.get.assert_called_once()
        self.mock_retriever.query.assert_not_called()

    def test_ask_question_empty(self) -> None:
        res = self.pipeline.ask_question("")
        self.assertEqual(res["answer"], "Please provide a question.")
        self.assertEqual(res["sources"], [])
        self.assertFalse(res["cached"])

    @patch("app.rag_pipeline.get_pipeline")
    def test_module_ask_question_interface(self, mock_get_pipeline: MagicMock) -> None:
        mock_pipeline_inst = MagicMock()
        mock_pipeline_inst.ask_question.return_value = {
            "answer": "Module answer",
            "sources": [],
            "cached": False,
        }
        mock_get_pipeline.return_value = mock_pipeline_inst

        res = ask_question("Test q")
        self.assertEqual(res["answer"], "Module answer")
        mock_pipeline_inst.ask_question.assert_called_once_with("Test q", use_cache=True, debug=False)


if __name__ == "__main__":
    unittest.main()
