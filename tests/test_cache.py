"""Unit test suite for app/cache.py."""

from __future__ import annotations

import time
import unittest
from pathlib import Path

from app.cache import AnswerCache, cache_key, normalize_question
from app.config import config

ROOT_DIR = Path(__file__).resolve().parent.parent
TEST_CACHE_PATH = ROOT_DIR / ".test_unit_cache.json"


class TestAnswerCache(unittest.TestCase):
    """Test suite for AnswerCache functionality."""

    def setUp(self) -> None:
        if TEST_CACHE_PATH.exists():
            TEST_CACHE_PATH.unlink()
        self.cache = AnswerCache(cache_path=TEST_CACHE_PATH, ttl_hours=1, enabled=True)

    def tearDown(self) -> None:
        if TEST_CACHE_PATH.exists():
            TEST_CACHE_PATH.unlink()

    def test_normalize_question(self) -> None:
        self.assertEqual(normalize_question("  Hello World?  "), "hello world")
        self.assertEqual(normalize_question("AI and ML!"), "ai and ml")
        self.assertEqual(normalize_question("Multiple   spaces"), "multiple spaces")

    def test_cache_put_get(self) -> None:
        question = "What deep learning projects has Vinay built?"
        answer = "Vinay built Fruit Freshness Classifier."
        sources = ["projects/fruit_freshness_classifier.md"]

        self.cache.put(question, answer, sources)
        result = self.cache.get(question)

        self.assertIsNotNone(result)
        self.assertEqual(result["answer"], answer)
        self.assertEqual(result["sources"], sources)
        self.assertTrue(result["cached"])

    def test_cache_miss(self) -> None:
        result = self.cache.get("Non-existent question?")
        self.assertIsNone(result)

    def test_cache_poisoned_entry_eviction(self) -> None:
        # Inject error message
        question = "Failed query"
        error_ans = "The AI service is temporarily unavailable. Please try again later."
        self.cache.put(question, error_ans, [])

        result = self.cache.get(question)
        self.assertIsNone(result)

    def test_cache_clear(self) -> None:
        self.cache.put("Q1", "A1", ["s1.md"])
        self.cache.put("Q2", "A2", ["s2.md"])
        cleared_count = self.cache.clear()
        self.assertEqual(cleared_count, 2)
        self.assertIsNone(self.cache.get("Q1"))


if __name__ == "__main__":
    unittest.main()
