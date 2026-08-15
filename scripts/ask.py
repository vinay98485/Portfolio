"""CLI for Portfolio RAG Assistant.

Flow:
    Question → Retriever → Cache check → Generator → Cache store → Return response

Usage:
    python scripts/ask.py "Tell me about Vinay"
    python scripts/ask.py --no-cache "What projects has Vinay built?"
    python scripts/ask.py --cache-stats
    python scripts/ask.py --clear-cache
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to sys.path if needed
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.cache import AnswerCache
from app.config import config
from app.rag_pipeline import ask_question


def configure_logging(level: str | None = None) -> None:
    logging.basicConfig(
        level=getattr(logging, (level or config.log_level).upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ask Vinay AI — Portfolio RAG Assistant.",
    )
    parser.add_argument("question", nargs="?", help="Question to ask.")
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Skip cache for this query.",
    )
    parser.add_argument(
        "--cache-stats",
        action="store_true",
        help="Print cache statistics and exit.",
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear the answer cache and exit.",
    )
    parser.add_argument(
        "--batch",
        type=Path,
        help="Path to a JSON file with a 'questions' array — run all questions.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode to view raw retrieval details.",
    )
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()

    # Cache-only operations
    if args.cache_stats or args.clear_cache:
        cache = AnswerCache()
        if args.cache_stats:
            print(json.dumps(cache.stats(), indent=2))
        if args.clear_cache:
            removed = cache.clear()
            print(json.dumps({"cleared": removed}))
        return

    # Batch mode
    if args.batch:
        if not args.batch.exists():
            print(f"Error: batch file not found: {args.batch}")
            raise SystemExit(1)
        data = json.loads(args.batch.read_text(encoding="utf-8"))
        questions = data.get("questions", [])
        results = []
        for q in questions:
            result = ask_question(q, use_cache=not args.no_cache, debug=args.debug)
            results.append({"question": q, **result})
        print(json.dumps(results, indent=2))
        return

    # Single question
    if not args.question:
        print("Error: provide a question, --batch file, --cache-stats, or --clear-cache")
        raise SystemExit(1)

    result = ask_question(args.question, use_cache=not args.no_cache, debug=args.debug)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
