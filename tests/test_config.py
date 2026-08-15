"""Unit test suite for app/config.py configuration validation and defaults."""

from __future__ import annotations

import unittest
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import ConfigurationError, load_config


class TestConfigValidation(unittest.TestCase):
    """Test suite for configuration loading, validation, and defaults."""

    def test_valid_config_loading(self) -> None:
        env = {
            "GEMINI_API_KEY": "test_api_key_12345",
        }
        cfg = load_config(validate=True, env=env)
        self.assertEqual(cfg.gemini_api_key, "test_api_key_12345")

    def test_missing_gemini_api_key_raises_error(self) -> None:
        env = {
            "GEMINI_API_KEY": "",
        }
        with self.assertRaises(ConfigurationError) as ctx:
            load_config(validate=True, env=env)

        self.assertIn("GEMINI_API_KEY", str(ctx.exception))
        self.assertIn("Missing required environment variable", str(ctx.exception))

    def test_config_defaults(self) -> None:
        env = {
            "GEMINI_API_KEY": "test_key",
        }
        cfg = load_config(validate=True, env=env)

        self.assertEqual(cfg.embedding_model, "sentence-transformers/paraphrase-MiniLM-L3-v2")
        self.assertEqual(cfg.chroma_db_path, ROOT_DIR / "database" / "chroma_db")
        self.assertEqual(cfg.top_k, 5)
        self.assertEqual(cfg.score_threshold, 1.6)
        self.assertTrue(cfg.cache_enabled)
        self.assertEqual(cfg.cache_ttl_hours, 168)

        # Backward compatibility properties
        self.assertEqual(cfg.embedding_model_name, "sentence-transformers/paraphrase-MiniLM-L3-v2")
        self.assertEqual(cfg.chroma_db_dir, ROOT_DIR / "database" / "chroma_db")
        self.assertEqual(cfg.similarity_threshold, 1.6)

    def test_custom_env_overrides(self) -> None:
        env = {
            "GEMINI_API_KEY": "override_key",
            "EMBEDDING_MODEL": "custom/embedding-model",
            "CHROMA_DB_PATH": "custom_db_path",
            "TOP_K": "10",
            "SCORE_THRESHOLD": "0.85",
            "CACHE_ENABLED": "false",
            "CACHE_TTL_HOURS": "24",
        }
        cfg = load_config(validate=True, env=env)

        self.assertEqual(cfg.gemini_api_key, "override_key")
        self.assertEqual(cfg.embedding_model, "custom/embedding-model")
        self.assertEqual(cfg.chroma_db_path, ROOT_DIR / "custom_db_path")
        self.assertEqual(cfg.top_k, 10)
        self.assertEqual(cfg.score_threshold, 0.85)
        self.assertFalse(cfg.cache_enabled)
        self.assertEqual(cfg.cache_ttl_hours, 24)

    def test_invalid_data_types_raise_configuration_error(self) -> None:
        env_bad_int = {
            "GEMINI_API_KEY": "key",
            "TOP_K": "not_an_int",
        }
        with self.assertRaises(ConfigurationError) as ctx:
            load_config(validate=True, env=env_bad_int)
        self.assertIn("TOP_K", str(ctx.exception))

        env_bad_float = {
            "GEMINI_API_KEY": "key",
            "SCORE_THRESHOLD": "invalid_float",
        }
        with self.assertRaises(ConfigurationError) as ctx:
            load_config(validate=True, env=env_bad_float)
        self.assertIn("SCORE_THRESHOLD", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
