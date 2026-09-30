"""Gateway configuration. Everything comes from the environment so the systemd
unit is the single source of truth and nothing operational lives in the code."""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _csv(name: str, default: str) -> tuple[str, ...]:
    raw = os.environ.get(name, default)
    return tuple(m.strip() for m in raw.split(",") if m.strip())


# The five models Module 6 uses. Requests for anything else are refused, so a
# student cannot reach a model the course has not budgeted for -- notably
# llama4:scout, which was disqualified on throughput grounds.
DEFAULT_MODELS = "qwen3:8b,gemma3:27b,gpt-oss:20b,llama3.2:3b,phi4:latest"


@dataclass(frozen=True)
class Settings:
    # --- upstream -----------------------------------------------------------
    ollama_url: str = field(default_factory=lambda:
        os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/"))
    upstream_timeout: float = field(default_factory=lambda:
        float(os.environ.get("UPSTREAM_TIMEOUT", "600")))

    # --- scheduling ---------------------------------------------------------
    # How many requests may execute against Ollama at once. Size this to the
    # GPU box, not to the class: three of the course models are 13-17 GB.
    max_concurrency: int = field(default_factory=lambda: _int("MAX_CONCURRENCY", 2))
    # Per student. One in flight means a student's own calls serialise, which is
    # what makes the global queue fair without any round-robin bookkeeping.
    per_student_inflight: int = field(default_factory=lambda: _int("PER_STUDENT_INFLIGHT", 1))
    # A runaway loop should get a clear 429, not unbounded memory on the box.
    per_student_queue: int = field(default_factory=lambda: _int("PER_STUDENT_QUEUE", 8))

    # --- access -------------------------------------------------------------
    tokens_file: str = field(default_factory=lambda:
        os.environ.get("TOKENS_FILE", "/etc/aicyber-gateway/tokens.json"))
    admin_token: str = field(default_factory=lambda: os.environ.get("ADMIN_TOKEN", ""))
    allowed_models: tuple[str, ...] = field(default_factory=lambda:
        _csv("ALLOWED_MODELS", DEFAULT_MODELS))

    # --- limits -------------------------------------------------------------
    max_prompt_chars: int = field(default_factory=lambda: _int("MAX_PROMPT_CHARS", 200_000))
    max_tokens_cap: int = field(default_factory=lambda: _int("MAX_TOKENS_CAP", 4096))


settings = Settings()
