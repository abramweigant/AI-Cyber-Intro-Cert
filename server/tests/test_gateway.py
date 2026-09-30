"""Gateway tests. No network and no Ollama: the upstream is faked.

The two that matter most are the fairness test and the cancellation test. The
latter covers a real leak found during the build, where a request cancelled while
queued never decremented the waiting counter, so that machine eventually got a
permanent spurious 429.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.update({
    # The tests simulate several student VMs, which needs X-Forwarded-For to be
    # believed. Production default is OFF -- test_forwarded_for_ignored_by_default
    # covers why, and it builds its own app to check it.
    "TRUST_FORWARDED_FOR": "1",
    "MAX_CONCURRENCY": "2",
    "PER_CLIENT_INFLIGHT": "1",
    "PER_CLIENT_QUEUE": "3",
    "MAX_TOKENS_CAP": "256",
    "ALLOWED_MODELS": "qwen3:8b,gemma3:27b",
})

from httpx import ASGITransport, AsyncClient           # noqa: E402
from aicyber_gateway.app import app, ollama, scheduler  # noqa: E402

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
        return ["qwen3:8b", "gemma3:27b", "llama3.2:3b", "llama4:scout"]

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
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://gw") as c:
        yield c


def vm(ip: str) -> dict:
    """Simulate a distinct student VM. _client_of() honours X-Forwarded-For."""
    return {"X-Forwarded-For": ip}


def body(model="qwen3:8b", **kw):
    return {"model": model, "messages": [{"role": "user", "content": "hi"}], **kw}


# --- no auth, by design -----------------------------------------------------
async def test_no_token_needed(client, fake):
    """Anything on the network may use it. If this ever starts returning 401,
    Module 6 Section 1.1 needs rewriting -- it teaches the opposite."""
    assert (await client.get("/v1/models")).status_code == 200
    assert (await client.post("/v1/chat/completions", json=body())).status_code == 200


class _Req:
    """Minimal stand-in for what _client_of() actually touches."""
    def __init__(self, headers, peer="10.9.9.9"):
        self.headers = headers
        self.client = type("C", (), {"host": peer})()


def test_forwarded_for_is_ignored_unless_trusted(monkeypatch):
    """The fairness bypass this guards against: with nothing in front of the
    gateway a client can set X-Forwarded-For itself, so a student varying it per
    request would take unlimited queue slots and starve the class. The header is
    therefore only believed when TRUST_FORWARDED_FOR is set."""
    import dataclasses
    from aicyber_gateway import app as appmod

    req = _Req({"x-forwarded-for": "1.2.3.4"}, peer="10.9.9.9")

    untrusted = dataclasses.replace(appmod.settings, trust_forwarded_for=False)
    monkeypatch.setattr(appmod, "settings", untrusted)
    assert appmod._client_of(req) == "10.9.9.9"        # spoof ignored

    trusted = dataclasses.replace(appmod.settings, trust_forwarded_for=True)
    monkeypatch.setattr(appmod, "settings", trusted)
    assert appmod._client_of(req) == "1.2.3.4"         # honoured behind a proxy

    # and with no header at all, either way
    bare = _Req({}, peer="10.9.9.9")
    assert appmod._client_of(bare) == "10.9.9.9"


def test_production_default_does_not_trust_forwarded_for():
    """Pins the default itself, independent of what the tests set."""
    import importlib
    import aicyber_gateway.config as cfg
    import os
    saved = os.environ.pop("TRUST_FORWARDED_FOR", None)
    try:
        importlib.reload(cfg)
        assert cfg.Settings().trust_forwarded_for is False
    finally:
        if saved is not None:
            os.environ["TRUST_FORWARDED_FOR"] = saved
        importlib.reload(cfg)


async def test_empty_allowlist_passes_everything_through(client, fake, monkeypatch):
    """Set ALLOWED_MODELS= (empty) when another course shares the box, so its
    models are not 403'd by a list that has nothing to do with them."""
    import dataclasses
    from aicyber_gateway import app as appmod

    monkeypatch.setattr(appmod, "settings",
                        dataclasses.replace(appmod.settings, allowed_models=()))

    r = await client.get("/v1/models")
    assert "llama4:scout" in [m["id"] for m in r.json()["data"]]
    r = await client.post("/v1/chat/completions", json=body(model="llama4:scout"))
    assert r.status_code == 200


# --- model allowlist --------------------------------------------------------
async def test_models_filtered_to_course_set(client, fake):
    r = await client.get("/v1/models")
    assert sorted(m["id"] for m in r.json()["data"]) == ["gemma3:27b", "qwen3:8b"]

async def test_disallowed_model_is_403(client, fake):
    r = await client.post("/v1/chat/completions", json=body(model="llama4:scout"))
    assert r.status_code == 403 and "not available" in r.json()["error"]["message"]


# --- request handling -------------------------------------------------------
async def test_streaming_refused(client, fake):
    r = await client.post("/v1/chat/completions", json=body(stream=True))
    assert r.status_code == 400

async def test_max_tokens_capped(client, fake):
    await client.post("/v1/chat/completions", json=body(max_tokens=99999))
    assert fake.payloads[-1]["max_tokens"] == 256
    assert fake.payloads[-1]["stream"] is False

async def test_missing_model_is_400(client, fake):
    r = await client.post("/v1/chat/completions",
                          json={"messages": [{"role": "user", "content": "hi"}]})
    assert r.status_code == 400

async def test_chat_passes_through(client, fake):
    r = await client.post("/v1/chat/completions", json=body())
    assert r.status_code == 200
    assert r.json()["choices"][0]["message"]["content"] == "ok"


# --- scheduling -------------------------------------------------------------
async def test_per_client_queue_limit_returns_429(client, fake):
    fake.delay = 0.35
    tasks = [asyncio.create_task(
        client.post("/v1/chat/completions", headers=vm("10.0.0.5"), json=body()))
        for _ in range(8)]                      # 1 in flight + 3 queued allowed
    codes = [r.status_code for r in await asyncio.gather(*tasks)]
    assert 429 in codes and 200 in codes, codes
    assert all(c in (200, 429) for c in codes), codes

async def test_one_vm_cannot_starve_another(client, fake):
    """10.0.0.1 bursts; 10.0.0.2's single request must not wait behind all of it."""
    fake.delay = 0.2
    order: list[str] = []

    async def go(ip, label):
        r = await client.post("/v1/chat/completions", headers=vm(ip), json=body())
        if r.status_code == 200:
            order.append(label)

    tasks = [asyncio.create_task(go("10.0.0.1", "burst")) for _ in range(4)]
    await asyncio.sleep(0.05)
    tasks.append(asyncio.create_task(go("10.0.0.2", "single")))
    await asyncio.gather(*tasks)

    assert "single" in order, order
    assert order.index("single") <= 1, order

async def test_queue_is_per_client_not_global(client, fake):
    """Four VMs sending one each must all succeed, even though any single VM
    would be rate-limited at four."""
    fake.delay = 0.1
    tasks = [asyncio.create_task(
        client.post("/v1/chat/completions", headers=vm(f"10.0.1.{i}"), json=body()))
        for i in range(1, 5)]
    codes = [r.status_code for r in await asyncio.gather(*tasks)]
    assert codes == [200, 200, 200, 200], codes

async def test_cancelled_while_queued_does_not_leak_waiting_count(client, fake):
    """Covers a real leak: cancel a queued request and the waiting counter was
    never decremented, so that VM eventually got a permanent spurious 429."""
    fake.delay = 0.5
    ip = "10.0.2.9"
    running = asyncio.create_task(
        client.post("/v1/chat/completions", headers=vm(ip), json=body()))
    await asyncio.sleep(0.05)
    queued = asyncio.create_task(
        client.post("/v1/chat/completions", headers=vm(ip), json=body()))
    await asyncio.sleep(0.05)
    queued.cancel()
    try:
        await queued
    except asyncio.CancelledError:
        pass
    await running
    await asyncio.sleep(0.05)
    assert scheduler._waiting.get(ip, 0) == 0, dict(scheduler._waiting)


# --- status endpoints -------------------------------------------------------
async def test_stats_is_open_and_attributes_by_client(client, fake):
    await client.post("/v1/chat/completions", headers=vm("10.0.3.7"), json=body())
    r = await client.get("/stats")
    assert r.status_code == 200
    assert "10.0.3.7" in r.json()["by_client"]

async def test_healthz(client, fake):
    r = await client.get("/healthz")
    assert r.status_code == 200 and r.json()["gateway"] == "ok"


# --- deployment flags -------------------------------------------------------
def test_run_sh_disables_uvicorn_proxy_headers_and_extra_workers():
    """Both flags are load-bearing and neither is visible from the code.

    uvicorn defaults proxy_headers=True, so without --no-proxy-headers uvicorn
    rewrites request.client from X-Forwarded-For before the gateway sees it, and
    a client can pick its own identity and take unlimited queue slots. This was
    a real bug: _client_of() gated the header correctly and the bypass still
    worked, because uvicorn had already done the rewrite underneath.

    --workers 1 matters because the queue lives in process memory; a second
    worker is a second independent queue.
    """
    run_sh = (Path(__file__).resolve().parent.parent / "run.sh").read_text()
    assert "--no-proxy-headers" in run_sh, "uvicorn would trust X-Forwarded-For"
    assert "--workers 1" in run_sh, "extra workers would multiply the concurrency cap"
