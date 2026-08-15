import logging
import time
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import config
from app.rag_pipeline import ask_question

# Configure logging
logger = logging.getLogger(__name__)

# 1. Initialize Limiter for Rate Limiting (10 req/min per IP)
limiter = Limiter(key_func=get_remote_address)

# 2. Initialize FastAPI Application
app = FastAPI(
    title="Vinay Portfolio AI Assistant",
    description="AI-powered portfolio assistant using Retrieval Augmented Generation.",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 3. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 4. Security Headers & API Logging Middleware
@app.middleware("http")
async def security_and_logging_middleware(request: Request, call_next: Any) -> Response:
    client_ip = request.client.host if (request.client and request.client.host) else "127.0.0.1"
    start_time = time.time()

    response = await call_next(request)

    process_time_ms = int(round((time.time() - start_time) * 1000))
    logger.info(
        f"API Request | Client IP: {client_ip} | Method: {request.method} | "
        f"Endpoint: {request.url.path} | Status: {response.status_code} | "
        f"Latency: {process_time_ms}ms"
    )

    # Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    return response


# 5. Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.error(f"Validation error on {request.method} {request.url.path}: {exc}")
    formatted_errors = []
    for err in exc.errors():
        err_copy = dict(err)
        if "ctx" in err_copy:
            err_copy["ctx"] = {k: str(v) for k, v in err_copy["ctx"].items()}
        formatted_errors.append(err_copy)

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid request payload or format.",
            "errors": formatted_errors,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception during {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred.",
            "error": str(exc),
        },
    )


# 6. Pydantic Models with Request Size & Field Protection
class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Recruiter question about Vinay's portfolio",
        json_schema_extra={"example": "What projects has Vinay built?"},
    )

    @field_validator("question")
    @classmethod
    def validate_question_content(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Question cannot be empty or whitespace only.")
        if len(cleaned) > 1000:
            raise ValueError("Question exceeds maximum length of 1000 characters.")
        return cleaned


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    cached: bool
    response_time_ms: int


# 7. Startup Event — log config summary and memory usage

@app.on_event("startup")
def on_startup() -> None:
    """Log application configuration on startup."""
    from app.rag_pipeline import get_memory_mb
    
    logger.info("=" * 60)
    logger.info("Vinay Portfolio AI Assistant v1.0.0 — Starting")
    logger.info(f"  Gemini Model     : {config.gemini_model}")
    logger.info(f"  Embedding Model  : {config.gemini_embedding_model}")
    logger.info(f"  ChromaDB Path    : {config.chroma_db_path}")
    logger.info(f"  Top K            : {config.top_k}")
    logger.info(f"  Score Threshold  : {config.score_threshold}")
    logger.info(f"  Cache Enabled    : {config.cache_enabled}")
    logger.info(f"  Cache TTL Hours  : {config.cache_ttl_hours}")
    logger.info(f"  Gemini API Key   : {'configured' if config.gemini_api_key else 'MISSING'}")
    logger.info("=" * 60)
    logger.info("Startup complete! Memory usage: %.2f MB", get_memory_mb())
    logger.info("=" * 60)


# 8. Endpoints

@app.get("/")
def root() -> dict[str, str]:
    """Root status endpoint."""
    return {
        "service": "Vinay Portfolio AI",
        "status": "running"
    }


@app.get("/health")
def health_check(response: Response) -> dict[str, Any]:
    """Health check endpoint evaluating system components.

    Returns HTTP 200 when all components are healthy.
    Returns HTTP 503 when any critical component is degraded.
    """
    config_status = "ok"
    db_status = "ok" if config.chroma_db_path.exists() else "error"
    llm_status = "ok" if config.gemini_api_key else "error"

    all_ok = config_status == "ok" and db_status == "ok" and llm_status == "ok"
    overall_status = "healthy" if all_ok else "unhealthy"

    if not all_ok:
        response.status_code = 503

    return {
        "status": overall_status,
        "components": {
            "config": config_status,
            "database": db_status,
            "llm": llm_status,
        },
    }


@app.post("/ask", response_model=AskResponse)
@limiter.limit("10/minute")
def ask_portfolio_question(request: Request, ask_req: AskRequest) -> dict[str, Any]:
    """Ask a question to the Portfolio RAG Assistant with rate limiting (10 req/min per IP)."""
    start_time = time.time()
    question_len = len(ask_req.question)
    client_ip = request.client.host if (request.client and request.client.host) else "127.0.0.1"
    
    logger.info(f"POST /ask from IP={client_ip} (len={question_len}): '{ask_req.question[:60]}'")

    try:
        result = ask_question(ask_req.question)
        elapsed_ms = int(round((time.time() - start_time) * 1000))
        logger.info(f"RAG question processed for IP={client_ip} in {elapsed_ms}ms | cached={result.get('cached')}")

        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "cached": result["cached"],
            "response_time_ms": elapsed_ms,
        }
    except Exception as e:
        logger.error(f"Failed to process RAG pipeline request for IP={client_ip}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while executing the RAG pipeline: {str(e)}",
        )


@app.get("/sample-questions", response_model=list[str])
def get_sample_questions() -> list[str]:
    """Return recruiter-focused sample questions."""
    return [
        "What projects has Vinay built?",
        "What deep learning projects has Vinay worked on?",
        "What technologies does Vinay know?",
        "Why should someone hire Vinay?",
        "What is Vinay's education background?",
    ]
