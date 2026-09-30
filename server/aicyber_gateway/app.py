"""AI-Cyber gateway: per-student auth, fair queueing, and a model allowlist in
front of Ollama on the course GPU box.

Serves the two paths Module 6 actually uses:
    GET  /v1/models              -- what discover_endpoint() probes
    POST /v1/chat/completions    -- what chat() posts

Plus /healthz (no auth) and /admin/stats (admin token).

A bad token on /v1/models must return 401, not 403: the course client keys its
"your token was rejected" message off that status, and retries everything else.
"""
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse

from .auth import TokenStore, bearer_from_header
from .config import settings
from .scheduler import QueueFull, Scheduler
from .upstream import Ollama, UpstreamError

log = logging.getLogger("aicyber.gateway")

store = TokenStore(settings.tokens_file)
scheduler = Scheduler(settings.max_concurrency, settings.per_student_inflight,
                      settings.per_student_queue)
ollama = Ollama(settings.ollama_url, settings.upstream_timeout)
STARTED_AT = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("gateway up: upstream=%s models=%s tokens=%d concurrency=%d",
             settings.ollama_url, ",".join(settings.allowed_models),
             store.count, settings.max_concurrency)
    if store.count == 0:
        log.warning("no tokens loaded from %s -- every request will 401",
                    settings.tokens_file)
    yield
    await ollama.aclose()


app = FastAPI(title="AI-Cyber Gateway", version="1.0", lifespan=lifespan,
              docs_url=None, redoc_url=None, openapi_url=None)


def _err(status: int, msg: str, **extra) -> JSONResponse:
    body = {"error": {"message": msg, "type": "gateway_error"}}
    body["error"].update(extra)
    return JSONResponse(body, status_code=status)


def _authenticate(authorization: str | None):
    """Returns (student, None) or (None, JSONResponse)."""
    token = bearer_from_header(authorization)
    if not token:
        return None, _err(401, "Missing bearer token. Put your issued token in "
                               "LLM_API_KEY in the .env file in the repository root.")
    student = store.verify(token)
    if student is None:
        return None, _err(401, "Token rejected. Check LLM_API_KEY in .env, then "
                               "restart the notebook kernel. If you believe it is "
                               "correct, it may have been revoked -- ask your instructor.")
    return student, None


# --------------------------------------------------------------------- health
@app.get("/healthz")
async def healthz():
    ok, detail = await ollama.healthy()
    return JSONResponse(
        {
            "gateway": "ok",
            "uptime_seconds": round(time.time() - STARTED_AT, 1),
            "upstream": {"url": settings.ollama_url, "reachable": ok, "detail": detail},
            "tokens_loaded": store.count,
            "in_flight": scheduler.in_flight,
        },
        status_code=200 if ok and store.count else 503,
    )


# ---------------------------------------------------------------------- admin
@app.get("/admin/stats")
async def admin_stats(authorization: str | None = Header(default=None)):
    if not settings.admin_token:
        return _err(503, "ADMIN_TOKEN is not configured on the gateway.")
    supplied = bearer_from_header(authorization)
    if supplied != settings.admin_token:
        return _err(401, "Admin token required.")
    ok, detail = await ollama.healthy()
    return {
        "upstream": {"url": settings.ollama_url, "reachable": ok, "detail": detail},
        "allowed_models": list(settings.allowed_models),
        "tokens_loaded": store.count,
        "uptime_seconds": round(time.time() - STARTED_AT, 1),
        **scheduler.stats(),
    }


# ------------------------------------------------------------------- /v1 API
@app.get("/v1/models")
async def list_models(authorization: str | None = Header(default=None)):
    student, err = _authenticate(authorization)
    if err:
        return err
    try:
        served = await ollama.list_models()
    except UpstreamError as e:
        return _err(e.status, e.detail)
    # Advertise only what the course is scoped to, so the notebook's
    # connectivity check reports on exactly the five models it needs.
    visible = [m for m in served if m in settings.allowed_models]
    missing = [m for m in settings.allowed_models if m not in served]
    if missing:
        log.warning("allowed models not pulled on the box: %s", missing)
    return {"object": "list", "data": [{"id": m, "object": "model",
                                        "owned_by": "aicyber"} for m in visible]}


@app.post("/v1/chat/completions")
async def chat_completions(request: Request,
                           authorization: str | None = Header(default=None)):
    student, err = _authenticate(authorization)
    if err:
        return err

    try:
        payload = await request.json()
    except Exception:
        return _err(400, "Request body must be JSON.")
    if not isinstance(payload, dict):
        return _err(400, "Request body must be a JSON object.")

    model = str(payload.get("model", "")).strip()
    if not model:
        return _err(400, "No 'model' in the request body.")
    if model not in settings.allowed_models:
        return _err(403, f"Model {model!r} is not available on this course endpoint.",
                    allowed=list(settings.allowed_models))

    if payload.get("stream"):
        return _err(400, "Streaming is not enabled on this gateway. Send "
                         "stream: false (the course client already does).")

    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages:
        return _err(400, "'messages' must be a non-empty list.")
    size = sum(len(str(m.get("content", ""))) for m in messages if isinstance(m, dict))
    if size > settings.max_prompt_chars:
        return _err(413, f"Prompt is {size:,} characters; the limit is "
                         f"{settings.max_prompt_chars:,}. Chunk it -- Module 6 "
                         f"Section 5.2 explains why you have to anyway.")

    # Cap output length so one request cannot monopolise a worker for minutes.
    try:
        want = int(payload.get("max_tokens") or settings.max_tokens_cap)
    except (TypeError, ValueError):
        want = settings.max_tokens_cap
    payload["max_tokens"] = max(1, min(want, settings.max_tokens_cap))
    payload["stream"] = False

    try:
        async with scheduler.slot(student.student_id, model) as queue_wait:
            t0 = time.monotonic()
            try:
                result = await ollama.chat(payload)
            except UpstreamError as e:
                log.warning("student=%s model=%s upstream_error=%s",
                            student.student_id, model, e.detail)
                return _err(e.status, e.detail)
            log.info("student=%s model=%s queue=%.2fs upstream=%.2fs",
                     student.student_id, model, queue_wait, time.monotonic() - t0)
            return result
    except QueueFull as e:
        return _err(429, f"You already have {e.waiting} requests queued (limit "
                         f"{e.limit}). Let the current ones finish -- the course "
                         f"client retries automatically.",
                    retry_after=15)
