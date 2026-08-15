"""Knowledge base ingestion pipeline for Portfolio RAG Assistant.

Reads markdown files recursively from knowledge/, chunks them,
generates embeddings with the configured Gemini Embedding model,
and stores them in database/chroma_db.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import chromadb

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import config
from app.embeddings import GeminiEmbeddingProvider

TARGET_MIN_WORDS = 300
TARGET_MAX_WORDS = 800

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
SECTION_FIELD_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)



@dataclass(frozen=True)
class Document:
    path: Path
    source: str
    doc_id: str
    content: str
    metadata: dict[str, str]


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    metadata: dict[str, str | int]


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def word_count(text: str) -> int:
    return len(re.findall(r"\b\S+\b", text))


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug or "document"


def stable_doc_id(source: str) -> str:
    return slugify(source.replace("/", "__").replace(".md", ""))


def read_markdown_files(knowledge_dir: Path) -> list[Path]:
    if not knowledge_dir.exists():
        raise FileNotFoundError(f"Knowledge directory does not exist: {knowledge_dir}")

    return sorted(
        path
        for path in knowledge_dir.rglob("*.md")
        if path.is_file() and not path.name.startswith(".")
    )


def extract_h1(content: str) -> str | None:
    for line in content.splitlines():
        match = HEADING_RE.match(line)
        if match and len(match.group(1)) == 1:
            return normalize_space(match.group(2))
    return None


def extract_section_lines(content: str, heading: str) -> list[str]:
    lines = content.splitlines()
    in_section = False
    values: list[str] = []

    for line in lines:
        match = SECTION_FIELD_RE.match(line)
        if match:
            current_heading = normalize_space(match.group(1)).lower()
            if in_section:
                break
            in_section = current_heading == heading.lower()
            continue

        if in_section:
            values.append(line)

    return values


def extract_section_value(content: str, heading: str) -> str | None:
    value = normalize_space("\n".join(extract_section_lines(content, heading)))
    return value or None


def extract_list_section(content: str, heading: str) -> list[str]:
    lines = extract_section_lines(content, heading)
    if not lines:
        return []

    values: list[str] = []
    for line in lines:
        clean = line.strip()
        if clean.startswith("- "):
            values.append(normalize_space(clean[2:]))
        elif clean and not clean.startswith("#"):
            values.append(normalize_space(clean))
    return [value for value in values if value]


def infer_type(path: Path) -> str:
    return "project" if "projects" in path.parts else "profile"


def infer_tags(metadata: dict[str, str], content: str) -> str:
    candidates: list[str] = []

    for key in ("category", "technologies", "project_name", "type"):
        value = metadata.get(key, "")
        if value:
            candidates.extend(part.strip() for part in re.split(r"[,/]", value))

    keyword_map = {
        "deep learning": ["deep learning", "cnn", "ann", "tensorflow", "keras"],
        "machine learning": ["machine learning", "xgboost", "scikit", "random forest"],
        "computer vision": ["computer vision", "image classification"],
        "streamlit": ["streamlit"],
        "django": ["django"],
        "sql": ["sql", "mysql"],
        "finance": ["bitcoin", "credit risk", "loan", "financial"],
        "customer analytics": ["customer", "churn", "segmentation", "cltv"],
    }
    content_lower = content.lower()
    for tag, needles in keyword_map.items():
        if any(needle in content_lower for needle in needles):
            candidates.append(tag)

    seen: set[str] = set()
    tags: list[str] = []
    for candidate in candidates:
        tag = normalize_space(candidate).lower()
        if tag and tag not in seen:
            seen.add(tag)
            tags.append(tag)

    return ", ".join(tags)


def extract_frontmatter(content: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}
    fm_text = match.group(1)
    fm = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm



def extract_metadata(path: Path, content: str, knowledge_dir: Path) -> dict[str, str]:
    fm = extract_frontmatter(content)
    
    source = path.relative_to(knowledge_dir).as_posix()
    doc_type = infer_type(path.relative_to(knowledge_dir))
    title = extract_h1(content) or path.stem.replace("_", " ").title()

    project_name = fm.get("project_name") or extract_section_value(content, "Project Name") if doc_type == "project" else None
    category = fm.get("category") or extract_section_value(content, "Category")
    domain = fm.get("domain")
    technologies = extract_list_section(content, "Technologies Used")

    metadata: dict[str, str] = {
        "source": source,
        "type": doc_type,
        "title": title,
    }
    
    if domain:
        metadata["domain"] = domain

    if doc_type == "project":
        metadata["project_name"] = project_name or title
        metadata["category"] = category or "project"
    else:
        metadata["category"] = category or path.stem.replace("_", " ")

    if technologies:
        metadata["technologies"] = ", ".join(technologies)

    metadata["tags"] = infer_tags(metadata, content)
    return metadata


def load_documents(knowledge_dir: Path) -> list[Document]:
    documents: list[Document] = []
    for path in read_markdown_files(knowledge_dir):
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            logging.warning("Skipping empty file: %s", path)
            continue

        source = path.relative_to(knowledge_dir).as_posix()
        metadata = extract_metadata(path, content, knowledge_dir)
        documents.append(
            Document(
                path=path,
                source=source,
                doc_id=stable_doc_id(source),
                content=content,
                metadata=metadata,
            )
        )
    return documents


def split_markdown_blocks(content: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []

    for line in content.splitlines():
        if HEADING_RE.match(line) and current:
            blocks.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)

    if current:
        blocks.append("\n".join(current).strip())

    return [block for block in blocks if block]


def split_long_block(block: str) -> list[str]:
    lines = block.splitlines()
    heading_lines: list[str] = []
    body_start = 0

    for index, line in enumerate(lines):
        if HEADING_RE.match(line):
            heading_lines.append(line)
            body_start = index + 1
        else:
            break

    prefix = "\n".join(heading_lines).strip()
    body = "\n".join(lines[body_start:]).strip()
    parts = re.split(r"\n\s*\n", body) if body else []

    chunks: list[str] = []
    current: list[str] = [prefix] if prefix else []

    for part in parts:
        candidate = "\n\n".join([*current, part]).strip()
        if current and word_count(candidate) > TARGET_MAX_WORDS:
            chunks.append("\n\n".join(current).strip())
            current = [prefix, part] if prefix else [part]
        else:
            current.append(part)

    if current:
        chunks.append("\n\n".join(current).strip())

    return [chunk for chunk in chunks if chunk]


def chunk_document(document: Document) -> list[Chunk]:
    blocks = split_markdown_blocks(document.content)
    raw_chunks: list[str] = []
    current: list[str] = []

    for block in blocks:
        block_words = word_count(block)

        if block_words > TARGET_MAX_WORDS:
            if current:
                raw_chunks.append("\n\n".join(current).strip())
                current = []
            raw_chunks.extend(split_long_block(block))
            continue

        candidate = "\n\n".join([*current, block]).strip()
        candidate_words = word_count(candidate)

        if current and candidate_words > TARGET_MAX_WORDS and word_count("\n\n".join(current)) >= TARGET_MIN_WORDS:
            raw_chunks.append("\n\n".join(current).strip())
            current = [block]
        else:
            current.append(block)

    if current:
        raw_chunks.append("\n\n".join(current).strip())

    chunks: list[Chunk] = []
    for index, text in enumerate(raw_chunks):
        text = text.strip()
        if not text:
            continue
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        chunk_id = f"{document.doc_id}::chunk-{index:04d}::{content_hash}"
        chunk_metadata: dict[str, str | int] = {
            **document.metadata,
            "doc_id": document.doc_id,
            "chunk_index": index,
            "chunk_words": word_count(text),
        }
        chunks.append(Chunk(chunk_id=chunk_id, text=text, metadata=chunk_metadata))

    return chunks


def get_collection(chroma_dir: Path, collection_name: str) -> Any:
    client = chromadb.PersistentClient(path=str(chroma_dir))
    return client.get_or_create_collection(
        name=collection_name,
        metadata={
            "embedding_model": config.embedding_model_name,
            "description": "Recruiter-facing portfolio knowledge base for Vinay Kumar Mandalapu.",
        },
    )


def delete_existing_document_chunks(collection: Any, doc_id: str) -> int:
    existing = collection.get(where={"doc_id": doc_id}, include=[])
    ids = existing.get("ids", [])
    if ids:
        collection.delete(ids=ids)
    return len(ids)


def batched(values: list[Chunk], batch_size: int) -> Iterable[list[Chunk]]:
    for start in range(0, len(values), batch_size):
        yield values[start : start + batch_size]


def ingest(
    knowledge_dir: Path | None = None,
    chroma_dir: Path | None = None,
    collection_name: str | None = None,
    batch_size: int = 64,
) -> dict[str, int]:
    k_dir = knowledge_dir or config.knowledge_dir
    c_dir = chroma_dir or config.chroma_db_dir
    c_name = collection_name or config.collection_name

    documents = load_documents(k_dir)
    if not documents:
        raise RuntimeError(f"No markdown documents found under {k_dir}")

    collection = get_collection(c_dir, c_name)
    logging.info("Active embedding model: %s", config.embedding_model_name)
    model = GeminiEmbeddingProvider(
        api_key=config.gemini_api_key,
        model_name=config.embedding_model_name
    )

    total_chunks = 0
    total_deleted = 0
    total_vectors = 0

    logging.info("Files discovered: %s", len(documents))

    for document in documents:
        chunks = chunk_document(document)
        if not chunks:
            logging.warning("No chunks generated for %s", document.source)
            continue

        deleted = delete_existing_document_chunks(collection, document.doc_id)
        total_deleted += deleted

        for batch in batched(chunks, batch_size):
            texts = [chunk.text for chunk in batch]
            embeddings = model.embed_documents(texts)

            collection.add(
                ids=[chunk.chunk_id for chunk in batch],
                documents=texts,
                metadatas=[chunk.metadata for chunk in batch],
                embeddings=embeddings,
            )
            total_vectors += len(batch)

        total_chunks += len(chunks)
        logging.info(
            "Processed %s | chunks=%s | replaced_vectors=%s",
            document.source,
            len(chunks),
            deleted,
        )

    summary = {
        "files_processed": len(documents),
        "chunks_generated": total_chunks,
        "vectors_stored": total_vectors,
        "vectors_replaced": total_deleted,
    }
    logging.info("Ingestion summary: %s", json.dumps(summary, sort_keys=True))
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest portfolio knowledge into ChromaDB.")
    parser.add_argument("--knowledge-dir", type=Path, default=config.knowledge_dir)
    parser.add_argument("--chroma-dir", type=Path, default=config.chroma_db_dir)
    parser.add_argument("--collection", default=config.collection_name)
    parser.add_argument("--batch-size", type=int, default=64)
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()

    try:
        summary = ingest(
            knowledge_dir=args.knowledge_dir,
            chroma_dir=args.chroma_dir,
            collection_name=args.collection,
            batch_size=args.batch_size,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
    except Exception:
        logging.exception("Ingestion failed")
        raise


if __name__ == "__main__":
    main()
