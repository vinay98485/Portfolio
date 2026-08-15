"""Script to verify application configuration and environment health.

Usage:
    python scripts/check_config.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import ConfigurationError, config, load_config


def check_configuration() -> bool:
    print("=" * 60)
    print("  Portfolio RAG Assistant — Configuration Health Check")
    print("=" * 60)

    all_passed = True

    # 1. Check .env file
    env_file = ROOT_DIR / ".env"
    if env_file.exists():
        print(f"  ✅ .env file loaded: {env_file}")
    else:
        print(f"  ⚠️  .env file NOT found at {env_file} (using system environment variables)")

    # 2. Check configuration validation & GEMINI_API_KEY
    try:
        cfg = load_config(validate=True)
        if cfg.gemini_api_key:
            masked_key = cfg.gemini_api_key[:6] + "..." + cfg.gemini_api_key[-4:] if len(cfg.gemini_api_key) > 10 else "***"
            print(f"  ✅ GEMINI_API_KEY: Configured ({masked_key})")
        else:
            print("  ❌ GEMINI_API_KEY: Missing or empty")
            all_passed = False
    except ConfigurationError as err:
        print(f"  ❌ GEMINI_API_KEY Error: {err}")
        all_passed = False

    # 3. Check ChromaDB path
    chroma_path = config.chroma_db_path
    if chroma_path.exists():
        print(f"  ✅ ChromaDB path: Exists at {chroma_path}")
    else:
        print(f"  ❌ ChromaDB path: Does NOT exist at {chroma_path} (Run: python ingestion/ingest.py)")
        all_passed = False

    # 4. Check Knowledge directory
    knowledge_path = config.knowledge_dir
    if knowledge_path.exists():
        files_count = len(list(knowledge_path.rglob("*.md")))
        print(f"  ✅ Knowledge directory: Exists at {knowledge_path} ({files_count} markdown files)")
    else:
        print(f"  ❌ Knowledge directory: Does NOT exist at {knowledge_path}")
        all_passed = False

    print("=" * 60)

    if all_passed:
        print("  🎉 All configuration checks passed successfully!")
        return True
    else:
        print("  ⚠️  Configuration checks failed. Please resolve the issues above.")
        return False


def main() -> None:
    success = check_configuration()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
