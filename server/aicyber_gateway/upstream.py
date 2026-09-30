"""Thin async client for Ollama's OpenAI-compatible surface.

Ollama serves /v1/chat/completions and /v1/models. It accepts (and ignores) an
Authorization header, which is exactly why this gateway exists.
"""
from __future__ import annotations

import httpx


class UpstreamError(Exception):
    def __init__(self, status: int, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.detail = detail


class Ollama:
    def __init__(self, base_url: str, timeout: float) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout, connect=10.0),
            limits=httpx.Limits(max_connections=32, max_keepalive_connections=8),
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def list_models(self) -> list[str]:
        try:
            r = await self._client.get("/v1/models")
        except httpx.RequestError as e:
            raise UpstreamError(502, f"cannot reach Ollama at {self.base_url}: {e}") from e
        if r.status_code != 200:
            raise UpstreamError(502, f"Ollama returned {r.status_code} for /v1/models")
        try:
            return sorted(m["id"] for m in r.json().get("data", []))
        except (ValueError, KeyError, TypeError) as e:
            raise UpstreamError(502, f"unreadable /v1/models payload: {e}") from e

    async def chat(self, payload: dict) -> dict:
        try:
            r = await self._client.post("/v1/chat/completions", json=payload)
        except httpx.TimeoutException as e:
            raise UpstreamError(504, f"Ollama timed out: {e}") from e
        except httpx.RequestError as e:
            raise UpstreamError(502, f"cannot reach Ollama: {e}") from e
        if r.status_code >= 400:
            # Pass the upstream's own message through -- a 404 here usually means
            # the model tag is not pulled on the box, and that is worth saying.
            snippet = r.text[:400].replace("\n", " ")
            raise UpstreamError(502 if r.status_code >= 500 else r.status_code,
                                f"Ollama returned {r.status_code}: {snippet}")
        try:
            return r.json()
        except ValueError as e:
            raise UpstreamError(502, f"Ollama returned non-JSON: {e}") from e

    async def healthy(self) -> tuple[bool, str]:
        try:
            r = await self._client.get("/v1/models", timeout=5.0)
            return (r.status_code == 200, f"HTTP {r.status_code}")
        except httpx.RequestError as e:
            return (False, str(e)[:160])
