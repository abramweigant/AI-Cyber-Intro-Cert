"""AI-Cyber gateway: a fair queue in front of Ollama on the course GPU box.

No authentication. Anything on the range that can reach this port may use it,
which is deliberate -- the gateway exists to stop ~20 students swamping one GPU,
not to keep anyone out. Module 6 Section 1.1 teaches students exactly that, and
what it would mean if this box were reachable from anywhere else.

Serves the two paths Module 6 uses:
    GET  /v1/models              -- what discover_endpoint() probes
    POST /v1/chat/completions    -- what chat() posts
plus /healthz and /stats, both open.
"""
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config import settings
from .scheduler import QueueFull, Scheduler
from .upstream import Ollama, UpstreamError

log = logging.getLogger("aicyber.gateway")

scheduler = Scheduler(settings.max_concurrency, settings.per_client_inflight,
                      settings.per_client_queue)
ollama = Ollama(settings.ollama_url, settings.upstream_timeout)
STARTED_AT = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("gateway up: upstream=%s concurrency=%d models=%s",
             settings.ollama_url, settings.max_concurrency,
             ",".join(settings.allowed_models))
    yield
    await ollama.aclose()


app = FastAPI(title="AI-Cyber Gateway", version="2.0", lifespan=lifespan,
              docs_url=None, redoc_url=None, openapi_url=None)


def _err(status: int, msg: str, **extra) -> JSONResponse:
    body = {"error": {"message": msg, "type": "gateway_error"}}
    body["error"].update(extra)
    return JSONResponse(body, status_code=status)


def _client_of(request: Request) -> str:
    """Which machine a request came from. One student VM per IP.

    X-Forwarded-For is only believed when TRUST_FORWARDED_FOR is set, because a
    client can set that header itself. Trusting it with nothing in front of the
    gateway would let a student vary it per request, take an unbounded number of
    queue slots, and starve the class -- defeating the only thing this service
    does. Enable it when a proxy you control is in front and rewriting it."""
    if settings.trust_forwarded_for:
        fwd = request.headers.get("x-forwarded-for", "")
        if fwd:
            return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# --------------------------------------------------------------------- status
@app.get("/healthz")
async def healthz():
    ok, detail = await ollama.healthy()
    return JSONResponse(
        {"gateway": "ok", "uptime_seconds": round(time.time() - STARTED_AT, 1),
         "upstream": {"url": settings.ollama_url, "reachable": ok, "detail": detail},
         "in_flight": scheduler.in_flight},
        status_code=200 if ok else 503)


@app.get("/stats")
async def stats():
    """Open on purpose: it is operational visibility on a private network, and
    knowing which VM is queueing is the point."""
    ok, detail = await ollama.healthy()
    return {"upstream": {"url": settings.ollama_url, "reachable": ok, "detail": detail},
            "allowed_models": list(settings.allowed_models) or "any (no allowlist)",
            "trust_forwarded_for": settings.trust_forwarded_for,
            "uptime_seconds": round(time.time() - STARTED_AT, 1),
            **scheduler.stats()}


# ------------------------------------------------------------------- /v1 API
@app.get("/v1/models")
async def list_models():
    try:
        served = await ollama.list_models()
    except UpstreamError as e:
        return _err(e.status, e.detail)
    missing = [m for m in settings.allowed_models if m not in served]
    if missing:
        log.warning("course models not pulled on the box: %s", missing)
    visible = served if not settings.allowed_models else [
        m for m in served if m in settings.allowed_models]
    return {"object": "list",
            "data": [{"id": m, "object": "model", "owned_by": "aicyber"}
                     for m in visible]}


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    client = _client_of(request)
    try:
        payload = await request.json()
    except Exception:
        return _err(400, "Request body must be JSON.")
    if not isinstance(payload, dict):
        return _err(400, "Request body must be a JSON object.")

    model = str(payload.get("model", "")).strip()
    if not model:
        return _err(400, "No 'model' in the request body.")
    if settings.allowed_models and model not in settings.allowed_models:
        return _err(403, f"Model {model!r} is not available on this endpoint.",
                    allowed=list(settings.allowed_models))
    if payload.get("stream"):
        return _err(400, "Streaming is not enabled on this gateway. Send "
                         "stream: false (the course client already does).")
    if not isinstance(payload.get("messages"), list) or not payload["messages"]:
        return _err(400, "'messages' must be a non-empty list.")

    # Cap output so one request cannot hold a worker for minutes.
    try:
        want = int(payload.get("max_tokens") or settings.max_tokens_cap)
    except (TypeError, ValueError):
        want = settings.max_tokens_cap
    payload["max_tokens"] = max(1, min(want, settings.max_tokens_cap))
    payload["stream"] = False

    try:
        async with scheduler.slot(client, model) as queue_wait:
            t0 = time.monotonic()
            try:
                result = await ollama.chat(payload)
            except UpstreamError as e:
                log.warning("client=%s model=%s upstream_error=%s", client, model, e.detail)
                return _err(e.status, e.detail)
            log.info("client=%s model=%s queue=%.2fs upstream=%.2fs",
                     client, model, queue_wait, time.monotonic() - t0)
            return result
    except QueueFull as e:
        return _err(429, f"This machine already has {e.waiting} requests queued "
                         f"(limit {e.limit}). Let them finish -- the course client "
                         f"retries automatically.", retry_after=15)
