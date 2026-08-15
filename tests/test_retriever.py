"""Test suite for the Portfolio RAG retriever.

Runs a battery of semantic queries against the live ChromaDB vector store
and validates that the retriever returns expected results.

Usage:
    python tests/test_retriever.py
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import config
from app.retriever import (
    PortfolioRetriever,
    RetrievalResult,
    l2_to_similarity,
)


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


def print_result_summary(result: RetrievalResult) -> None:
    """Pretty-print key fields of a retrieval result."""
    status = "✅ FOUND" if result.found else "❌ NOT FOUND"
    print(f"  Status      : {status}")
    print(f"  Query       : {result.query}")
    print(f"  Results     : {result.total_results}")
    if result.message:
        print(f"  Message     : {result.message}")
    for r in result.results:
        print(
            f"    #{r['rank']}  {r['source']:<55} "
            f"sim={r['similarity_score']:.4f}  dist={r['distance']:.4f}  "
            f"title={r['metadata'].get('title', 'N/A')}"
        )


TESTS: list[dict] = [
    # --- Expected to FIND results ---
    {
        "name": "Deep learning projects",
        "question": "What deep learning projects has Vinay built?",
        "expect_found": True,
        "expect_sources_contain": ["fruit_freshness_classifier.md", "bank_customer_churn_prediction.md"],
        "expect_category": "project",
        "expect_domain": "deep_learning",
    },
    {
        "name": "Machine learning projects",
        "question": "What machine learning projects has Vinay built?",
        "expect_found": True,
        "expect_sources_contain": ["bitcoin_price_prediction.md"],
        "expect_category": "project",
        "expect_domain": "machine_learning",
    },
    {
        "name": "About Vinay",
        "question": "Tell me about Vinay",
        "expect_found": True,
        "expect_sources_contain": ["about_me.md"],
    },
    {
        "name": "Technologies and skills",
        "question": "Python TensorFlow Keras Scikit-learn programming languages and skills",
        "expect_found": True,
        "expect_sources_contain": ["skills.md"],
        "expect_category": "skills",
    },
    {
        "name": "Education",
        "question": "What is Vinay's educational background?",
        "expect_found": True,
        "expect_sources_contain": ["education.md"],
        "expect_category": "education",
    },
    {
        "name": "Certifications",
        "question": "What certifications does Vinay have?",
        "expect_found": True,
        "expect_sources_contain": ["certifications.md"],
    },
    {
        "name": "Contact information",
        "question": "How can I contact Vinay?",
        "expect_found": True,
        "expect_sources_contain": ["contact.md"],
    },
    {
        "name": "Credit risk project",
        "question": "Tell me about the credit risk scoring engine project",
        "expect_found": True,
        "expect_sources_contain": ["credit_risk_scoring_engine.md"],
    },
    {
        "name": "Bitcoin project",
        "question": "How does the Bitcoin price prediction project work?",
        "expect_found": True,
        "expect_sources_contain": ["bitcoin_price_prediction.md"],
    },
    {
        "name": "Churn prediction",
        "question": "Explain the bank customer churn prediction project",
        "expect_found": True,
        "expect_sources_contain": ["bank_customer_churn_prediction.md"],
    },
    {
        "name": "Strongest projects",
        "question": "What are Vinay's strongest projects?",
        "expect_found": True,
        "expect_sources_contain": [],
    },
    {
        "name": "Why hire Vinay",
        "question": "Why should I hire Vinay?",
        "expect_found": True,
        "expect_sources_contain": [],
    },
    # --- Expected to NOT find results (irrelevant queries) ---
    {
        "name": "Irrelevant: cooking recipes",
        "question": "What is the best recipe for chocolate cake?",
        "expect_found": False,
        "expect_sources_contain": [],
    },
    # --- Edge cases ---
    {
        "name": "Edge: empty question",
        "question": "",
        "expect_found": False,
        "expect_sources_contain": [],
    },
    {
        "name": "Edge: whitespace only",
        "question": "   ",
        "expect_found": False,
        "expect_sources_contain": [],
    },
]


def run_tests() -> None:
    configure_logging()

    retriever = PortfolioRetriever()

    separator("Collection Stats")
    stats = retriever.get_collection_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    passed = 0
    failed = 0
    total = len(TESTS)

    for test in TESTS:
        separator(f"TEST: {test['name']}")
        result = retriever.query(test["question"])
        print_result_summary(result)

        errors: list[str] = []

        if result.found != test["expect_found"]:
            errors.append(
                f"Expected found={test['expect_found']}, got found={result.found}"
            )

        if test["expect_found"] and test["expect_sources_contain"]:
            returned_sources = {
                r["source"].split("/")[-1] for r in result.results
            }
            for expected_src in test["expect_sources_contain"]:
                if expected_src not in returned_sources:
                    errors.append(
                        f"Expected source '{expected_src}' not in results: {returned_sources}"
                    )

        if result.found:
            for r in result.results:
                required_keys = {"rank", "chunk_id", "text", "similarity_score", "distance", "metadata", "source"}
                missing = required_keys - set(r.keys())
                if missing:
                    errors.append(f"Result missing keys: {missing}")
                if r["similarity_score"] < 0 or r["similarity_score"] > 1:
                    errors.append(f"Similarity score out of range: {r['similarity_score']}")
                
                expected_category = test.get("expect_category")
                if expected_category and r["metadata"].get("category") != expected_category:
                    errors.append(f"Expected category '{expected_category}', got '{r['metadata'].get('category')}'")

                expected_domain = test.get("expect_domain")
                if expected_domain and r["metadata"].get("domain") != expected_domain:
                    errors.append(f"Expected domain '{expected_domain}', got '{r['metadata'].get('domain')}'")

        try:
            json_str = result.to_json()
            parsed = json.loads(json_str)
            if parsed["found"] != result.found:
                errors.append("JSON round-trip mismatch on 'found'")
        except (json.JSONDecodeError, KeyError) as exc:
            errors.append(f"JSON serialization error: {exc}")

        if errors:
            failed += 1
            for err in errors:
                print(f"  ❌ FAIL: {err}")
        else:
            passed += 1
            print(f"  ✅ PASS")

    # Test: configurable top_k
    separator("TEST: Configurable top_k=3")
    result = retriever.query("Tell me about Vinay's projects", top_k=3)
    if result.total_results <= 3:
        print(f"  ✅ PASS — returned {result.total_results} results (max 3)")
        passed += 1
    else:
        print(f"  ❌ FAIL — returned {result.total_results} results, expected ≤3")
        failed += 1
    total += 1

    # Test: restrictive threshold
    separator("TEST: Very restrictive threshold=0.1")
    result = retriever.query("What projects has Vinay built?", score_threshold=0.1)
    if not result.found:
        print(f"  ✅ PASS — no results with ultra-tight threshold")
        passed += 1
    else:
        print(f"  ❌ FAIL — expected no results with threshold=0.1, got {result.total_results}")
        failed += 1
    total += 1

    # Test: permissive threshold
    separator("TEST: Permissive threshold=4.0")
    result = retriever.query("What projects has Vinay built?", score_threshold=4.0)
    if result.found and result.total_results > 0:
        print(f"  ✅ PASS — permissive threshold returned {result.total_results} results")
        passed += 1
    else:
        print(f"  ❌ FAIL — expected results with permissive threshold")
        failed += 1
    total += 1

    # Test: l2_to_similarity helper
    separator("TEST: l2_to_similarity conversion")
    sim_errors: list[str] = []
    if abs(l2_to_similarity(0.0) - 1.0) > 1e-6:
        sim_errors.append(f"l2_to_similarity(0.0) = {l2_to_similarity(0.0)}, expected 1.0")
    if abs(l2_to_similarity(2.0) - 0.0) > 1e-6:
        sim_errors.append(f"l2_to_similarity(2.0) = {l2_to_similarity(2.0)}, expected 0.0")
    if abs(l2_to_similarity(4.0) - 0.0) > 1e-6:
        sim_errors.append(f"l2_to_similarity(4.0) = {l2_to_similarity(4.0)}, expected 0.0 (clamped)")
    if l2_to_similarity(1.0) < 0 or l2_to_similarity(1.0) > 1:
        sim_errors.append(f"l2_to_similarity(1.0) out of range")
    if sim_errors:
        for err in sim_errors:
            print(f"  ❌ FAIL: {err}")
        failed += 1
    else:
        print(f"  ✅ PASS — all similarity conversions correct")
        passed += 1
    total += 1

    separator("SUMMARY")
    print(f"  Total : {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print()

    if failed:
        print("⚠️  Some tests failed.")
        sys.exit(1)
    else:
        print("🎉 All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    run_tests()
