"""Gateway configuration, all from the environment with usable defaults.

Deliberately small: this runs on a private range network where anything that can
reach the box may use it. The gateway exists to keep 20 students from swamping
one GPU, not to keep anyone out.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


# The five models Module 6 uses. Requests for anything else are refused -- not as
# a security control, but so one student cannot invoke llama4:scout (~5-15 tok/s)
# and wreck throughput for the whole class.
DEFAULT_MODELS = "qwen3:8b,gemma3:27b,gpt-oss:20b,llama3.2:3b,phi4:latest"


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

    allowed_models: tuple[str, ...] = field(default_factory=lambda: tuple(
        m.strip() for m in os.environ.get("ALLOWED_MODELS", DEFAULT_MODELS).split(",")
        if m.strip()))
    max_tokens_cap: int = field(default_factory=lambda: _int("MAX_TOKENS_CAP", 4096))


settings = Settings()
