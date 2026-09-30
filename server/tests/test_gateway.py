"""Gateway tests. No network and no Ollama: the upstream is faked.

The ones that matter most are the auth-status test (Module 6's client keys its
error message off 401 specifically), the fairness test, and the cancellation
test -- that last one covers a real leak found during the build, where a request
cancelled while queued never decremented the waiting counter and every later
request for that student eventually got a spurious 429.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import stat
import sys
import tempfile
import time
from pathlib import Path

import pytest

SERVER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SERVER_DIR))

# --- environment must be set before the app module is imported --------------
TOKENS = {
    "alice": "alice-token-aaaaaaaaaaaaaaaa",
    "bob":   "bob-token-bbbbbbbbbbbbbbbbbb",
    "carol": "carol-token-cccccccccccccccc",   # revoked below
}
_tmpdir = tempfile.mkdtemp()
_tokens_path = os.path.join(_tmpdir, "tokens.json")
with open(_tokens_path, "w") as fh:
    json.dump({"students": [
        {"student_id": "alice", "token_hash": hashlib.sha256(TOKENS["alice"].encode()).hexdigest()},
        {"student_id": "bob",   "token_hash": hashlib.sha256(TOKENS["bob"].encode()).hexdigest()},
        {"student_id": "carol", "token_hash": hashlib.sha256(TOKENS["carol"].encode()).hexdigest(),
         "disabled": True},
    ]}, fh)
os.chmod(_tokens_path, stat.S_IRUSR | stat.S_IWUSR)

os.environ.update({
    "TOKENS_FILE": _tokens_path,
    "ADMIN_TOKEN": "admin-secret",
    "MAX_CONCURRENCY": "2",
    "PER_STUDENT_INFLIGHT": "1",
    "PER_STUDENT_QUEUE": "3",
    "MAX_TOKENS_CAP": "256",
    "MAX_PROMPT_CHARS": "5000",
    "ALLOWED_MODELS": "qwen3:8b,gemma3:27b",
})

from httpx import ASGITransport, AsyncClient           # noqa: E402
from aicyber_gateway.app import app, ollama, scheduler  # noqa: E402

pytestmark = pytest.mark.asyncio


# --- fake upstream ----------------------------------------------------------
class Fake:
    def __init__(self):
        self.calls, self.delay, self.payloads = 0, 0.0, []

    async def chat(self, payload):
        self.calls += 1
        self.payloads.append(payload)
        if self.delay:
            await asyncio.sleep(self.delay)
        return {"choices": [{"message": {"role": "assistant", "content": "ok"}}]}

    async def list_models(self):
        return ["qwen3:8b", "gemma3:27b", "llama3.2:3b", "some-other-model"]

    async def healthy(self):
        return True, "HTTP 200"


@pytest.fixture
def fake(monkeypatch):
    f = Fake()
    monkeypatch.setattr(ollama, "chat", f.chat)
    monkeypatch.setattr(ollama, "list_models", f.list_models)
    monkeypatch.setattr(ollama, "healthy", f.healthy)
    return f


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://gw") as c:
        yield c


def auth(who: str) -> dict:
    return {"Authorization": f"Bearer {TOKENS[who]}"}


def body(model="qwen3:8b", **kw):
    return {"model": model, "messages": [{"role": "user", "content": "hi"}], **kw}


# --- authentication ---------------------------------------------------------
async def test_missing_token_is_401(client, fake):
    assert (await client.get("/v1/models")).status_code == 401


async def test_bad_token_is_401_not_403(client, fake):
    """Module 6's discover_endpoint() raises its 'token rejected' message only
    on 401. A 403 here would send students chasing the wrong problem."""
    r = await client.get("/v1/models", headers={"Authorization": "Bearer nope"})
    assert r.status_code == 401
    assert "LLM_API_KEY" in r.json()["error"]["message"]


async def test_revoked_token_is_401(client, fake):
    assert (await client.get("/v1/models", headers=auth("carol"))).status_code == 401


async def test_bare_token_without_bearer_prefix_works(client, fake):
    r = await client.get("/v1/models", headers={"Authorization": TOKENS["alice"]})
    assert r.status_code == 200


async def test_revocation_is_picked_up_without_restart(client, fake):
    assert (await client.get("/v1/models", headers=auth("bob"))).status_code == 200
    data = json.load(open(_tokens_path))
    for s in data["students"]:
        if s["student_id"] == "bob":
            s["disabled"] = True
    time.sleep(0.01)                      # ensure a distinct mtime
    with open(_tokens_path, "w") as fh:
        json.dump(data, fh)
    assert (await client.get("/v1/models", headers=auth("bob"))).status_code == 401
    for s in data["students"]:            # restore for other tests
        if s["student_id"] == "bob":
            s["disabled"] = False
    time.sleep(0.01)
    with open(_tokens_path, "w") as fh:
        json.dump(data, fh)


# --- model allowlist --------------------------------------------------------
async def test_models_are_filtered_to_the_allowlist(client, fake):
    r = await client.get("/v1/models", headers=auth("alice"))
    ids = sorted(m["id"] for m in r.json()["data"])
    assert ids == ["gemma3:27b", "qwen3:8b"]        # llama3.2:3b not allowed here

async def test_disallowed_model_is_403(client, fake):
    r = await client.post("/v1/chat/completions", headers=auth("alice"),
                          json=body(model="llama4:scout"))
    assert r.status_code == 403
    assert "not available" in r.json()["error"]["message"]


# --- request validation -----------------------------------------------------
async def test_streaming_is_refused(client, fake):
    r = await client.post("/v1/chat/completions", headers=auth("alice"),
                          json=body(stream=True))
    assert r.status_code == 400 and "Streaming" in r.json()["error"]["message"]

async def test_oversized_prompt_is_413(client, fake):
    r = await client.post("/v1/chat/completions", headers=auth("alice"),
                          json={"model": "qwen3:8b",
                                "messages": [{"role": "user", "content": "x" * 6000}]})
    assert r.status_code == 413

async def test_max_tokens_is_capped(client, fake):
    await client.post("/v1/chat/completions", headers=auth("alice"),
                      json=body(max_tokens=99999))
    assert fake.payloads[-1]["max_tokens"] == 256
    assert fake.payloads[-1]["stream"] is False

async def test_missing_model_is_400(client, fake):
    r = await client.post("/v1/chat/completions", headers=auth("alice"),
                          json={"messages": [{"role": "user", "content": "hi"}]})
    assert r.status_code == 400


# --- happy path -------------------------------------------------------------
async def test_chat_passes_through(client, fake):
    r = await client.post("/v1/chat/completions", headers=auth("alice"), json=body())
    assert r.status_code == 200
    assert r.json()["choices"][0]["message"]["content"] == "ok"


# --- scheduling -------------------------------------------------------------
async def test_per_student_queue_limit_returns_429(client, fake):
    fake.delay = 0.35
    tasks = [asyncio.create_task(
        client.post("/v1/chat/completions", headers=auth("alice"), json=body()))
        for _ in range(8)]                       # limit is 1 in flight + 3 queued
    results = await asyncio.gather(*tasks)
    codes = [r.status_code for r in results]
    assert 429 in codes, codes
    assert 200 in codes, codes
    assert all(c in (200, 429) for c in codes), codes

async def test_one_student_cannot_starve_another(client, fake):
    """alice fires a burst; bob's single request must not wait behind all of it."""
    fake.delay = 0.2
    order: list[str] = []

    async def go(who):
        r = await client.post("/v1/chat/completions", headers=auth(who), json=body())
        if r.status_code == 200:
            order.append(who)
        return r.status_code

    tasks = [asyncio.create_task(go("alice")) for _ in range(4)]
    await asyncio.sleep(0.05)                    # alice is already running
    tasks.append(asyncio.create_task(go("bob")))
    await asyncio.gather(*tasks)

    assert "bob" in order, order
    # With one in-flight per student, bob gets the second global slot immediately
    # rather than queueing behind alice's remaining three.
    assert order.index("bob") <= 1, order

async def test_cancelled_while_queued_does_not_leak_waiting_count(client, fake):
    """The bug this covers: cancel a queued request and the waiting counter never
    decremented, so alice eventually got a permanent spurious 429."""
    fake.delay = 0.5
    running = asyncio.create_task(
        client.post("/v1/chat/completions", headers=auth("alice"), json=body()))
    await asyncio.sleep(0.05)
    queued = asyncio.create_task(
        client.post("/v1/chat/completions", headers=auth("alice"), json=body()))
    await asyncio.sleep(0.05)
    queued.cancel()
    try:
        await queued
    except asyncio.CancelledError:
        pass
    await running
    await asyncio.sleep(0.05)
    assert scheduler._waiting.get("alice", 0) == 0, dict(scheduler._waiting)


# --- admin / health ---------------------------------------------------------
async def test_admin_stats_requires_the_admin_token(client, fake):
    assert (await client.get("/admin/stats")).status_code == 401
    assert (await client.get("/admin/stats", headers=auth("alice"))).status_code == 401
    r = await client.get("/admin/stats", headers={"Authorization": "Bearer admin-secret"})
    assert r.status_code == 200
    assert "capacity" in r.json() and "by_student" in r.json()

async def test_healthz_needs_no_auth(client, fake):
    r = await client.get("/healthz")
    assert r.status_code == 200 and r.json()["gateway"] == "ok"
