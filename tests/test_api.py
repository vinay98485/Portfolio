"""Unit test suite for FastAPI API layer, rate limiting, and security features."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app, limiter


class TestAPIProtection(unittest.TestCase):
    """Test suite for API endpoints, rate limiting, security headers, and validation."""

    def setUp(self) -> None:
        self.client = TestClient(app)

    @patch("app.main.ask_question")
    def test_allowed_request(self, mock_ask_question: unittest.mock.MagicMock) -> None:
        """Verify that a valid POST /ask request succeeds and returns 200."""
        mock_ask_question.return_value = {
            "answer": "Vinay has built several projects including Fruit Freshness Classifier.",
            "sources": ["projects/fruit_freshness_classifier.md"],
            "cached": False,
        }

        response = self.client.post("/ask", json={"question": "What projects has Vinay built?"})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("answer", data)
        self.assertIn("sources", data)
        self.assertIn("cached", data)
        self.assertIn("response_time_ms", data)
        self.assertEqual(data["sources"], ["projects/fruit_freshness_classifier.md"])

    def test_security_headers(self) -> None:
        """Verify that security headers are injected into all HTTP responses."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(response.headers.get("X-XSS-Protection"), "1; mode=block")

    def test_invalid_input_empty_body(self) -> None:
        """Verify that an empty POST body returns 422 validation error."""
        response = self.client.post("/ask", json={})
        self.assertEqual(response.status_code, 422)

    def test_invalid_input_short_question(self) -> None:
        """Verify that questions under 3 characters return 422 validation error."""
        response = self.client.post("/ask", json={"question": "hi"})
        self.assertEqual(response.status_code, 422)

    def test_invalid_input_whitespace(self) -> None:
        """Verify that whitespace-only questions return 422 validation error."""
        response = self.client.post("/ask", json={"question": "   "})
        self.assertEqual(response.status_code, 422)

    def test_invalid_input_overly_long_question(self) -> None:
        """Verify that questions exceeding 1000 characters return 422 validation error."""
        long_question = "What " * 250  # 1250 characters
        response = self.client.post("/ask", json={"question": long_question})
        self.assertEqual(response.status_code, 422)

    @patch("app.main.ask_question")
    def test_rate_limit_exceeded(self, mock_ask_question: unittest.mock.MagicMock) -> None:
        """Verify that exceeding 10 requests per minute triggers 429 Too Many Requests."""
        mock_ask_question.return_value = {
            "answer": "Mocked answer",
            "sources": [],
            "cached": True,
        }

        # Reset limiter state to ensure clean rate limit testing
        limiter.reset()

        responses = []
        for i in range(12):
            res = self.client.post("/ask", json={"question": f"Question {i}?"})
            responses.append(res.status_code)

        # The first 10 requests should succeed (200), and subsequent requests should return 429
        self.assertIn(429, responses)
        self.assertEqual(responses.count(429), 2)


if __name__ == "__main__":
    unittest.main()
