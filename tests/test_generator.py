"""Test suite for the generation layer.

Tests the full pipeline: config → cache → context building → Gemini → answer.
Separates offline (unit) tests from online (Gemini API) tests.

Usage:
    python tests/test_generator.py               # run all tests
    python tests/test_generator.py --offline     # skip Gemini API tests
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.cache import AnswerCache, cache_key, normalize_question
from app.config import config, load_config
from app.generator import (
    FALLBACK_ANSWER,
    MAX_ATTEMPTS,
    RETRY_DELAYS,
    RETRYABLE_STATUS_CODES,
    TEMPORARILY_UNAVAILABLE,
    GenerationResult,
    PortfolioGenerator,
    build_context,
    extract_sources,
    is_cacheable,
    is_valid_cached_answer,
    _is_retryable,
)

logger = logging.getLogger(__name__)
TEST_CACHE_PATH = ROOT_DIR / ".test_answer_cache.json"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def separator(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  ✅ {name}")
    else:
        FAILED += 1
        msg = f"  ❌ {name}"
        if detail:
            msg += f" — {detail}"
        print(msg)


SAMPLE_CHUNKS = [
    {
        "rank": 1,
        "chunk_id": "about-me::chunk-0000::abc123",
        "text": "# About Vinay\n\nVinay Kumar Mandalapu is a CS student focused on AI/ML.",
        "similarity_score": 0.45,
        "distance": 1.1,
        "metadata": {
            "source": "about_me.md",
            "type": "profile",
            "title": "About Vinay Kumar Mandalapu",
            "category": "about me",
        },
        "source": "about_me.md",
    },
    {
        "rank": 2,
        "chunk_id": "skills::chunk-0000::def456",
        "text": "# Skills\n\n## Programming Languages\n- Python\n- Java\n- C",
        "similarity_score": 0.38,
        "distance": 1.24,
        "metadata": {
            "source": "skills.md",
            "type": "profile",
            "title": "Skills",
            "category": "skills",
        },
        "source": "skills.md",
    },
    {
        "rank": 3,
        "chunk_id": "projects-fruit::chunk-0000::ghi789",
        "text": "# Fruit Freshness Classifier\n\nDeep Learning CNN with 99.01% accuracy.",
        "similarity_score": 0.32,
        "distance": 1.36,
        "metadata": {
            "source": "projects/fruit_freshness_classifier.md",
            "type": "project",
            "title": "Fruit Freshness Classifier",
            "category": "Deep Learning",
            "project_name": "Fruit Freshness Classifier",
        },
        "source": "projects/fruit_freshness_classifier.md",
    },
]


def test_config() -> None:
    separator("Config loading")
    cfg = load_config()
    check("Config loads", cfg is not None)
    check("API key is set", bool(cfg.gemini_api_key), "GEMINI_API_KEY missing")
    check("top_k is int", isinstance(cfg.top_k, int))
    check("temperature is float", isinstance(cfg.temperature, float))
    check("cache_enabled is bool", isinstance(cfg.cache_enabled, bool))
    check(
        "cache_ttl_hours is positive",
        cfg.cache_ttl_hours > 0,
        f"got {cfg.cache_ttl_hours}",
    )
    check("model name set", bool(cfg.gemini_model))
    print(f"  Config: model={cfg.gemini_model}, top_k={cfg.top_k}, temp={cfg.temperature}")


def test_normalize_question() -> None:
    separator("Question normalisation")
    check(
        "Strips whitespace",
        normalize_question("  hello  ") == "hello",
    )
    check(
        "Lowercases",
        normalize_question("HELLO WORLD") == "hello world",
    )
    check(
        "Removes all punctuation",
        normalize_question("What is AI, exactly?!") == "what is ai exactly",
    )
    check(
        "Collapses whitespace",
        normalize_question("  lots   of   spaces  ") == "lots of spaces",
    )
    check(
        "Same key for variations",
        cache_key("Tell me about Vinay?")
        == cache_key("  tell me about vinay  "),
    )
    check(
        "Different key for different questions",
        cache_key("Tell me about Vinay")
        != cache_key("What projects has Vinay built"),
    )


def test_answer_cache() -> None:
    separator("Answer cache")

    if TEST_CACHE_PATH.exists():
        TEST_CACHE_PATH.unlink()

    cache = AnswerCache(cache_path=TEST_CACHE_PATH, ttl_hours=1, enabled=True)

    result = cache.get("unknown question")
    check("Cache miss returns None", result is None)

    cache.put("What is AI?", "AI is cool.", ["about_me.md"])
    hit = cache.get("What is AI?")
    check("Cache hit after put", hit is not None)
    check(
        "Hit returns correct answer",
        hit is not None and hit["answer"] == "AI is cool.",
    )
    check(
        "Hit returns correct sources",
        hit is not None and hit["sources"] == ["about_me.md"],
    )
    check(
        "Hit marks cached=True",
        hit is not None and hit.get("cached") is True,
    )

    hit2 = cache.get("  what is AI?  ")
    check("Normalised question hits same entry", hit2 is not None)

    stats = cache.stats()
    check("Stats returns dict", isinstance(stats, dict))
    check("Stats shows 1 active", stats.get("active_entries") == 1)

    key = cache_key("What is AI?")
    raw_entry = cache._store.get(key, {})
    check(
        "Entry has question_hash field",
        raw_entry.get("question_hash") == key,
    )
    check(
        "Entry has created_at ISO timestamp",
        isinstance(raw_entry.get("created_at"), str)
        and "T" in raw_entry.get("created_at", ""),
    )

    expired_cache = AnswerCache(
        cache_path=ROOT_DIR / ".test_expired_cache.json",
        ttl_hours=0,
        enabled=True,
    )
    expired_cache.put("old question", "old answer", ["old.md"])
    time.sleep(0.1)
    expired_result = expired_cache.get("old question")
    check("Expired entry returns None", expired_result is None)

    disabled_cache = AnswerCache(cache_path=TEST_CACHE_PATH, enabled=False)
    disabled_cache.put("anything", "anything", [])
    check("Disabled cache get returns None", disabled_cache.get("anything") is None)

    poison_cache = AnswerCache(
        cache_path=ROOT_DIR / ".test_poison_cache.json",
        ttl_hours=1,
        enabled=True,
    )
    poison_cache.put(
        "What certs?",
        "Sorry, I encountered an error generating the answer: 503 UNAVAILABLE",
        ["certs.md"],
    )
    poison_hit = poison_cache.get("What certs?")
    check("Poisoned legacy error entry returns None", poison_hit is None)

    poison_cache.put("Temp fail", TEMPORARILY_UNAVAILABLE, ["x.md"])
    temp_hit = poison_cache.get("Temp fail")
    check("Poisoned TEMPORARILY_UNAVAILABLE returns None", temp_hit is None)

    poison_cache.put("Empty q", "", ["x.md"])
    empty_hit = poison_cache.get("Empty q")
    check("Poisoned empty entry returns None", empty_hit is None)

    cache.clear()
    check("Cache clear empties store", cache.get("What is AI?") is None)

    for p in [
        TEST_CACHE_PATH,
        ROOT_DIR / ".test_expired_cache.json",
        ROOT_DIR / ".test_poison_cache.json",
    ]:
        if p.exists():
            p.unlink()


def test_build_context() -> None:
    separator("Context building")

    context = build_context(SAMPLE_CHUNKS, max_chunks=3)
    check("Context is non-empty", len(context) > 0)
    check("Contains Source 1", "[Source 1:" in context)
    check("Contains Source 2", "[Source 2:" in context)
    check("Contains source file", "about_me.md" in context)
    check("Contains chunk text", "Vinay Kumar Mandalapu" in context)
    check("Contains project name", "Fruit Freshness Classifier" in context)

    limited = build_context(SAMPLE_CHUNKS, max_chunks=1)
    check("max_chunks=1 limits output", "Source 2" not in limited)

    empty = build_context([], max_chunks=5)
    check("Empty chunks returns empty string", empty == "")


def test_extract_sources() -> None:
    separator("Source extraction")

    sources = extract_sources(SAMPLE_CHUNKS)
    check("Returns 3 unique sources", len(sources) == 3)
    check("about_me.md in sources", "about_me.md" in sources)
    check("skills.md in sources", "skills.md" in sources)

    dupes = SAMPLE_CHUNKS + [SAMPLE_CHUNKS[0]]
    deduped = extract_sources(dupes)
    check("Deduplicates sources", len(deduped) == 3)


def test_generation_result() -> None:
    separator("GenerationResult serialisation")

    result = GenerationResult(
        answer="Test answer",
        sources=["a.md", "b.md"],
        question="Test?",
        cached=False,
        retrieval_found=True,
        chunks_used=2,
        model="gemini-2.5-flash",
    )
    d = result.to_dict()
    check("to_dict has answer", d["answer"] == "Test answer")
    check("to_dict has sources", d["sources"] == ["a.md", "b.md"])

    j = result.to_json()
    parsed = json.loads(j)
    check("to_json round-trips", parsed["answer"] == "Test answer")


def test_fallback_without_gemini() -> None:
    separator("Fallback (no Gemini call)")

    gen = PortfolioGenerator()

    result = gen.generate(
        question="Something irrelevant",
        retrieval_results=[],
        retrieval_found=False,
    )
    check(
        "Fallback returns correct message",
        result.answer == FALLBACK_ANSWER,
    )
    check("Fallback has no sources", result.sources == [])
    check("Fallback marks retrieval_found=False", result.retrieval_found is False)
    check("Fallback marks chunks_used=0", result.chunks_used == 0)

    result2 = gen.generate(
        question="Another question",
        retrieval_results=[],
        retrieval_found=True,
    )
    check(
        "Empty results triggers fallback",
        result2.answer == FALLBACK_ANSWER,
    )


def test_is_cacheable() -> None:
    separator("is_cacheable / is_valid_cached_answer")

    good = GenerationResult(
        answer="Vinay is a CS student focused on AI/ML.",
        sources=["about_me.md"],
        retrieval_found=True,
        chunks_used=2,
    )
    check("Successful result is cacheable", is_cacheable(good))

    unavail = GenerationResult(
        answer=TEMPORARILY_UNAVAILABLE,
        sources=["about_me.md"],
        retrieval_found=True,
        chunks_used=2,
    )
    check("TEMPORARILY_UNAVAILABLE is NOT cacheable", not is_cacheable(unavail))

    empty = GenerationResult(
        answer="",
        sources=["about_me.md"],
        retrieval_found=True,
        chunks_used=2,
    )
    check("Empty answer is NOT cacheable", not is_cacheable(empty))

    ws = GenerationResult(
        answer="   ",
        sources=["about_me.md"],
        retrieval_found=True,
        chunks_used=1,
    )
    check("Whitespace answer is NOT cacheable", not is_cacheable(ws))

    fallback = GenerationResult(
        answer=FALLBACK_ANSWER,
        sources=[],
        retrieval_found=True,
        chunks_used=0,
    )
    check("Fallback answer is NOT cacheable", not is_cacheable(fallback))

    no_ret = GenerationResult(
        answer=FALLBACK_ANSWER,
        sources=[],
        retrieval_found=False,
        chunks_used=0,
    )
    check("retrieval_found=False is NOT cacheable", not is_cacheable(no_ret))

    check(
        "Valid cached answer passes",
        is_valid_cached_answer("Vinay is great."),
    )
    check(
        "TEMPORARILY_UNAVAILABLE cached answer fails",
        not is_valid_cached_answer(TEMPORARILY_UNAVAILABLE),
    )
    check(
        "Legacy error cached answer fails",
        not is_valid_cached_answer("Sorry, I encountered an error generating the answer: 503"),
    )
    check(
        "Empty cached answer fails",
        not is_valid_cached_answer(""),
    )
    check(
        "Whitespace cached answer fails",
        not is_valid_cached_answer("   "),
    )


def test_retry_mechanism() -> None:
    separator("Retry mechanism (mocked)")

    for code in [429, 500, 502, 503, 504]:
        mock_exc = Exception(f"{code} Server Error")
        mock_exc.status_code = code  # type: ignore[attr-defined]
        check(f"Status {code} is retryable", _is_retryable(mock_exc))

    for code in [400, 401, 403, 404]:
        mock_exc = Exception(f"{code} Client Error")
        mock_exc.status_code = code  # type: ignore[attr-defined]
        check(f"Status {code} is NOT retryable", not _is_retryable(mock_exc))

    check("RETRY_DELAYS is [1, 2, 4]", RETRY_DELAYS == [1, 2, 4])
    check("MAX_ATTEMPTS is 4", MAX_ATTEMPTS == 4)
    check(
        "RETRYABLE_STATUS_CODES correct",
        RETRYABLE_STATUS_CODES == {429, 500, 502, 503, 504},
    )


def test_gemini_503_retry_and_not_cached() -> None:
    separator("Gemini 503 retry + failure NOT cached")

    gen = PortfolioGenerator()

    with patch.object(gen, "_call_gemini") as mock_call:
        exc_503 = Exception("503 UNAVAILABLE")
        exc_503.status_code = 503  # type: ignore[attr-defined]
        mock_call.side_effect = exc_503

        result = gen.generate(
            question="What projects has Vinay built?",
            retrieval_results=SAMPLE_CHUNKS,
            retrieval_found=True,
        )

        check(
            "503 failure returns TEMPORARILY_UNAVAILABLE",
            result.answer == TEMPORARILY_UNAVAILABLE,
        )
        check(
            "503 failure has sources (from retrieval)",
            len(result.sources) > 0,
        )
        check(
            "503 failure is NOT cacheable",
            not is_cacheable(result),
        )

    test_cache = AnswerCache(
        cache_path=ROOT_DIR / ".test_503_cache.json",
        ttl_hours=1,
        enabled=True,
    )
    if is_cacheable(result):
        test_cache.put("What projects?", result.answer, result.sources)

    check(
        "Failed response was NOT stored in cache",
        test_cache.get("What projects?") is None,
    )

    cache_path = ROOT_DIR / ".test_503_cache.json"
    if cache_path.exists():
        cache_path.unlink()


def test_gemini_success_mocked() -> None:
    separator("Gemini successful generation (mocked)")

    gen = PortfolioGenerator()

    with patch.object(gen, "_call_gemini") as mock_call:
        mock_call.return_value = "Vinay has built 7 impressive projects including a CNN classifier."

        result = gen.generate(
            question="What projects has Vinay built?",
            retrieval_results=SAMPLE_CHUNKS,
            retrieval_found=True,
        )

        check("Mocked success returns answer", "projects" in result.answer.lower())
        check("Mocked success is cacheable", is_cacheable(result))
        check("Mocked success has sources", len(result.sources) > 0)
        check("Mocked success has chunks_used > 0", result.chunks_used > 0)
        check("Mocked success has cached=False", result.cached is False)


def test_cache_hit_and_expiry() -> None:
    separator("Cache hit and expiry flow")

    cache_path = ROOT_DIR / ".test_hit_expiry_cache.json"
    if cache_path.exists():
        cache_path.unlink()

    cache = AnswerCache(cache_path=cache_path, ttl_hours=1, enabled=True)

    cache.put(
        "What skills does Vinay have?",
        "Vinay knows Python, Java, TensorFlow, and more.",
        ["skills.md"],
    )

    hit = cache.get("What skills does Vinay have?")
    check("Cache hit returns answer", hit is not None)
    check(
        "Cache hit answer is correct",
        hit is not None and hit["answer"] == "Vinay knows Python, Java, TensorFlow, and more.",
    )
    check(
        "Cache hit sources correct",
        hit is not None and hit["sources"] == ["skills.md"],
    )

    expired_cache = AnswerCache(cache_path=cache_path, ttl_hours=0, enabled=True)
    time.sleep(0.1)
    expired = expired_cache.get("What skills does Vinay have?")
    check("Expired entry returns None", expired is None)

    if cache_path.exists():
        cache_path.unlink()


def test_gemini_generation() -> None:
    separator("Gemini generation (LIVE API)")

    gen = PortfolioGenerator()

    result = gen.generate(
        question="Tell me about Vinay",
        retrieval_results=SAMPLE_CHUNKS,
        retrieval_found=True,
    )
    check("Answer is non-empty", len(result.answer) > 0)
    check("Answer is not fallback", result.answer != FALLBACK_ANSWER)
    check(
        "Answer is not temporarily unavailable",
        result.answer != TEMPORARILY_UNAVAILABLE,
    )
    check("Sources populated", len(result.sources) > 0)
    check("chunks_used > 0", result.chunks_used > 0)
    check("Model is set", bool(result.model))
    check("Result is cacheable", is_cacheable(result))

    print(f"\n  Answer preview: {result.answer[:200]}…")
    print(f"  Sources: {result.sources}")


def test_full_pipeline() -> None:
    separator("Full pipeline (RAGPipeline)")

    from app.rag_pipeline import RAGPipeline

    test_cache = AnswerCache(
        cache_path=ROOT_DIR / ".test_pipeline_cache.json",
        ttl_hours=1,
        enabled=True,
    )

    pipeline = RAGPipeline(cache=test_cache)

    result = pipeline.ask_question("Tell me about Vinay")
    check("Pipeline returns answer", "answer" in result)
    check("Pipeline returns sources", "sources" in result)
    check("Answer is non-empty", len(result.get("answer", "")) > 0)
    print(f"\n  Answer: {result['answer'][:200]}…")
    print(f"  Sources: {result.get('sources', [])}")

    result2 = pipeline.ask_question("Tell me about Vinay")
    check("Second call hits cache", result2.get("cached") is True)
    check("Cached answer matches", result2["answer"] == result["answer"])

    result3 = pipeline.ask_question("What is the best chocolate cake recipe?")
    check(
        "Irrelevant question gets fallback",
        FALLBACK_ANSWER in result3.get("answer", ""),
    )
    check("Fallback has no sources", result3.get("sources") == [])

    result4 = pipeline.ask_question("")
    check("Empty question handled", "answer" in result4)

    result5 = pipeline.ask_question("Tell me about Vinay", use_cache=False)
    check("no-cache returns answer", len(result5.get("answer", "")) > 0)
    check("no-cache not marked cached", result5.get("cached") is not True)

    test_cache_path = ROOT_DIR / ".test_pipeline_cache.json"
    if test_cache_path.exists():
        test_cache_path.unlink()


def test_hallucination_guard() -> None:
    separator("Hallucination guard (LIVE API)")

    gen = PortfolioGenerator()

    trick_chunks = [
        {
            "rank": 1,
            "chunk_id": "contact::chunk-0000::abc",
            "text": "# Contact\n\n- Name: Vinay kumar Mandalapu\n- Location: Hyderabad",
            "similarity_score": 0.3,
            "distance": 1.4,
            "metadata": {"source": "contact.md", "title": "Contact"},
            "source": "contact.md",
        }
    ]
    result = gen.generate(
        question="What PhD degree does Vinay have?",
        retrieval_results=trick_chunks,
        retrieval_found=True,
    )
    answer_lower = result.answer.lower()
    has_phd_claim = "vinay has a phd" in answer_lower or "vinay holds a phd" in answer_lower
    check(
        "Does NOT hallucinate a PhD",
        not has_phd_claim,
        f"Answer: {result.answer[:150]}",
    )
    mentions_missing = any(
        phrase in answer_lower
        for phrase in ["couldn't find", "not found", "no information", "not mention", "doesn't mention", "does not mention", "not available", "no mention"]
    )
    check(
        "Acknowledges missing information",
        mentions_missing,
        f"Answer: {result.answer[:150]}",
    )


def run_tests(offline_only: bool = False) -> None:
    global PASSED, FAILED
    configure_logging()

    test_config()
    test_normalize_question()
    test_answer_cache()
    test_build_context()
    test_extract_sources()
    test_generation_result()
    test_fallback_without_gemini()
    test_is_cacheable()
    test_retry_mechanism()
    test_gemini_503_retry_and_not_cached()
    test_gemini_success_mocked()
    test_cache_hit_and_expiry()

    if offline_only:
        separator("SKIPPED: Online tests (--offline flag)")
    else:
        test_gemini_generation()
        test_full_pipeline()
        test_hallucination_guard()

    separator("SUMMARY")
    total = PASSED + FAILED
    print(f"  Total : {total}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print()

    if FAILED:
        print("⚠️  Some tests failed.")
        sys.exit(1)
    else:
        print("🎉 All tests passed!")
        sys.exit(0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Test the generation layer.")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip tests that call the Gemini API.",
    )
    args = parser.parse_args()
    run_tests(offline_only=args.offline)


if __name__ == "__main__":
    main()
