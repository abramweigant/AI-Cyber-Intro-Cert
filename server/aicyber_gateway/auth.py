"""Per-student bearer tokens, stored as SHA-256 hashes.

Ollama has no authentication of any kind, so this module is the only thing
standing between the student VMs and the GPU box. Module 6 Section 1.1 teaches
that explicitly; if you change the semantics here, that section needs re-reading.

The plaintext token is never stored. issue_token.py prints it once at mint time.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import threading
import time
from dataclasses import dataclass


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Student:
    student_id: str
    token_hash: str
    disabled: bool = False
    note: str = ""


class TokenStore:
    """Reads tokens.json, and reloads it when the file changes on disk so you can
    issue or revoke a token without restarting the service mid-class."""

    def __init__(self, path: str) -> None:
        self.path = path
        self._lock = threading.Lock()
        self._by_hash: dict[str, Student] = {}
        self._mtime: float = -1.0
        self.reload(force=True)

    # -- loading ------------------------------------------------------------
    def reload(self, force: bool = False) -> None:
        try:
            mtime = os.path.getmtime(self.path)
        except OSError:
            with self._lock:
                self._by_hash, self._mtime = {}, -1.0
            return
        if not force and mtime == self._mtime:
            return
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
        except (OSError, json.JSONDecodeError):
            # A malformed file must not silently empty the store mid-class;
            # keep whatever was loaded last and let /healthz surface staleness.
            return
        entries = raw.get("students", raw) if isinstance(raw, dict) else raw
        loaded: dict[str, Student] = {}
        for e in entries or []:
            th = str(e.get("token_hash", "")).lower()
            if len(th) != 64:
                continue
            loaded[th] = Student(
                student_id=str(e.get("student_id", "unknown")),
                token_hash=th,
                disabled=bool(e.get("disabled", False)),
                note=str(e.get("note", "")),
            )
        with self._lock:
            self._by_hash, self._mtime = loaded, mtime

    # -- lookup -------------------------------------------------------------
    def verify(self, token: str) -> Student | None:
        """Constant-time comparison against every known hash.

        A plain dict lookup would be faster, but it compares the *hash* of an
        attacker-supplied value, so the timing channel it leaks is not useful.
        We still use compare_digest per candidate: with 20 students it costs
        nothing and it is the habit a security course should model."""
        if not token:
            return None
        self.reload()
        candidate = hash_token(token)
        with self._lock:
            students = list(self._by_hash.values())
        for s in students:
            if hmac.compare_digest(candidate, s.token_hash):
                return None if s.disabled else s
        return None

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._by_hash)

    @property
    def loaded_at(self) -> float:
        with self._lock:
            return self._mtime


def bearer_from_header(value: str | None) -> str:
    """Accept 'Bearer <token>' and a bare token, because students will paste both."""
    if not value:
        return ""
    parts = value.split(None, 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return value.strip()
