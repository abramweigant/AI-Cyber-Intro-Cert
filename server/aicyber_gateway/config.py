"""Gateway configuration, all from the environment with usable defaults.

Deliberately small: this runs on a private range network where anything that can
reach the box may use it. The gateway exists to keep 20 students from swamping
one GPU, not to keep anyone out.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def _int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


# The five models Module 6 uses. Requests for anything else are refused -- not as
# a security control, but so one student cannot invoke llama4:scout (~5-15 tok/s)
# and wreck throughput for the whole class.
#
# Set ALLOWED_MODELS to an EMPTY string to allow whatever Ollama is serving. Do
# that if someone else's course shares this box and pulls its own models --
# otherwise their requests get a 403 from a list that has nothing to do with them.
# gemma3:27b was dropped 2026-10-09: 17 GB will not fit the range's 16 GB vGPU
# (GRID A100D-16C), so it ran on partial CPU offload. gpt-oss:20b (13 GB) is the
# largest that fits and took over as Module 6's capstone model.
DEFAULT_MODELS = "qwen3:8b,gpt-oss:20b,llama3.2:3b,phi4:latest"


@dataclass(frozen=True)
class Settings:
    ollama_url: str = field(default_factory=lambda:
        os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/"))
    upstream_timeout: float = field(default_factory=lambda:
        float(os.environ.get("UPSTREAM_TIMEOUT", "600")))

    # How many requests may execute against Ollama at once. Size to the box's
    # VRAM, not to the class: three course models are 13-17 GB.
    max_concurrency: int = field(default_factory=lambda: _int("MAX_CONCURRENCY", 2))
    # Per client IP. One in flight means a student's own calls serialise, which is
    # what makes the global queue fair without any round-robin bookkeeping.
    per_client_inflight: int = field(default_factory=lambda: _int("PER_CLIENT_INFLIGHT", 1))
    # A runaway loop gets a clear 429 rather than unbounded memory on the box.
    per_client_queue: int = field(default_factory=lambda: _int("PER_CLIENT_QUEUE", 8))

    # Empty tuple means "no allowlist": pass through whatever Ollama serves.
    allowed_models: tuple[str, ...] = field(default_factory=lambda: tuple(
        m.strip() for m in os.environ.get("ALLOWED_MODELS", DEFAULT_MODELS).split(",")
        if m.strip()))
    max_tokens_cap: int = field(default_factory=lambda: _int("MAX_TOKENS_CAP", 4096))

    # Whether to believe X-Forwarded-For when deciding which machine a request
    # came from. Default FALSE, and that matters: with nothing in front of the
    # gateway, any client can set that header itself, and a student who varies it
    # per request gets unlimited concurrency and starves everyone else. Enable it
    # only when a proxy you control is actually in front and rewriting it.
    trust_forwarded_for: bool = field(default_factory=lambda: _bool("TRUST_FORWARDED_FOR"))


settings = Settings()
