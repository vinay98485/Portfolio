"""Vector database rebuild script for Portfolio RAG Assistant.

Wipes existing database/chroma_db and re-runs ingestion.
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import config
from ingestion.ingest import configure_logging, ingest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild the ChromaDB portfolio vector store.")
    parser.add_argument("--knowledge-dir", type=Path, default=config.knowledge_dir)
    parser.add_argument("--chroma-dir", type=Path, default=config.chroma_db_dir)
    parser.add_argument("--collection", default=config.collection_name)
    parser.add_argument("--batch-size", type=int, default=64)
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()

    try:
        if args.chroma_dir.exists():
            logging.info("Removing existing vector database: %s", args.chroma_dir)
            shutil.rmtree(args.chroma_dir)

        summary = ingest(
            knowledge_dir=args.knowledge_dir,
            chroma_dir=args.chroma_dir,
            collection_name=args.collection,
            batch_size=args.batch_size,
        )
        logging.info("Rebuild complete")
        print(json.dumps(summary, indent=2, sort_keys=True))
    except Exception:
        logging.exception("Vector database rebuild failed")
        raise


if __name__ == "__main__":
    main()
