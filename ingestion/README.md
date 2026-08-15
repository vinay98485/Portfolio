# Ingestion Workflow

This directory contains the scripts for processing markdown documents from `knowledge/` and creating vector embeddings inside `database/chroma_db`.

## Changing the Embedding Model

If you decide to optimize memory usage by changing the embedding model (for example, from `sentence-transformers/all-MiniLM-L6-v2` to `sentence-transformers/paraphrase-MiniLM-L3-v2`), you **must** follow these steps to avoid dimension mismatch errors in ChromaDB. Existing embeddings are tied to the dimensions output by the older model.

### 1. Delete old ChromaDB

Because the new embedding model likely outputs vectors of a different size or distribution, the old database must be removed:
```bash
rm -rf database/chroma_db
```

### 2. Update the Model Configuration

Update your `.env` (or `.env.example`) file:
```env
EMBEDDING_MODEL=sentence-transformers/paraphrase-MiniLM-L3-v2
```

### 3. Rebuild Embeddings & Ingest Knowledge Again

Run the ingestion script to parse the `knowledge/` folder using the newly active model. This will create a fresh `chroma_db` database and store the newly generated embeddings.

```bash
python3 -m ingestion.ingest
```

## Logs

The ingestion script will log the active embedding model being loaded when the pipeline starts:
```
Active embedding model: sentence-transformers/paraphrase-MiniLM-L3-v2
```
