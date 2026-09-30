"""Fair scheduling across students.

The policy is "one request in flight per student, round-robin between students",
and it falls out of two nested semaphores rather than any explicit round-robin
bookkeeping:

  * a per-student semaphore of size 1 means a student's own calls serialise, so
    a student can never hold more than one place in the global queue;
  * asyncio.Semaphore wakes waiters in FIFO order, so the global queue -- which
    therefore contains at most one entry per student -- is served round-robin.

That is the whole trick. Module 6 Section 3 fires ~75 sequential calls; without
the per-student cap those 75 would sit ahead of everyone else in a global FIFO
and one student would own the class's GPU for the duration.
"""
from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager


class QueueFull(Exception):
    """Raised when a student already has too many requests waiting.

    A runaway loop should get an immediate, explanatory 429 -- which the course
    client retries with backoff -- rather than quietly consuming memory."""

    def __init__(self, waiting: int, limit: int) -> None:
        super().__init__(f"{waiting} requests already queued for this token (limit {limit})")
        self.waiting = waiting
        self.limit = limit


class Scheduler:
    def __init__(self, max_concurrency: int, per_student_inflight: int,
                 per_student_queue: int) -> None:
        self.max_concurrency = max(1, max_concurrency)
        self.per_student_inflight = max(1, per_student_inflight)
        self.per_student_queue = max(1, per_student_queue)

        # Semaphores belong to the event loop that created them. uvicorn runs one
        # loop for the life of the process, so in production these are made once
        # -- but binding lazily and rebuilding on a loop change keeps the
        # component usable from a second loop (tests, an embedded runner) instead
        # of failing with "bound to a different event loop" deep inside acquire().
        self._loop: asyncio.AbstractEventLoop | None = None
        self._global = asyncio.Semaphore(self.max_concurrency)
        self._student_sems: dict[str, asyncio.Semaphore] = {}
        self._waiting: dict[str, int] = defaultdict(int)

        # metrics
        self.in_flight = 0
        self.served = 0
        self.rejected_queue_full = 0
        self.errors = 0
        self.per_model: dict[str, int] = defaultdict(int)
        self.per_student: dict[str, int] = defaultdict(int)
        self._latencies: deque[float] = deque(maxlen=512)
        self._waits: deque[float] = deque(maxlen=512)

    # ------------------------------------------------------------------ slots
    def _bind_loop(self) -> None:
        """Rebuild loop-bound state if the running loop changed.

        Only the semaphores and the in-flight/waiting counters are loop-bound.
        Cumulative metrics are not, and are deliberately preserved."""
        loop = asyncio.get_running_loop()
        if self._loop is loop:
            return
        self._loop = loop
        self._global = asyncio.Semaphore(self.max_concurrency)
        self._student_sems.clear()
        self._waiting.clear()
        self.in_flight = 0

    def _sem_for(self, student_id: str) -> asyncio.Semaphore:
        sem = self._student_sems.get(student_id)
        if sem is None:
            sem = asyncio.Semaphore(self.per_student_inflight)
            self._student_sems[student_id] = sem
        return sem

    @asynccontextmanager
    async def slot(self, student_id: str, model: str = ""):
        """Acquire the right to make one upstream call. Raises QueueFull."""
        self._bind_loop()
        if self._waiting[student_id] >= self.per_student_queue:
            self.rejected_queue_full += 1
            raise QueueFull(self._waiting[student_id], self.per_student_queue)

        queued_at = time.monotonic()
        self._waiting[student_id] += 1
        admitted = False          # did we reach the inner block and decrement?
        student_sem = self._sem_for(student_id)
        try:
            async with student_sem:          # one in flight per student
                async with self._global:     # bounded load on the GPU box
                    self._waiting[student_id] -= 1
                    admitted = True
                    wait = time.monotonic() - queued_at
                    self._waits.append(wait)
                    self.in_flight += 1
                    started = time.monotonic()
                    try:
                        yield wait
                        self.served += 1
                        if model:
                            self.per_model[model] += 1
                        self.per_student[student_id] += 1
                    except Exception:
                        self.errors += 1
                        raise
                    finally:
                        self.in_flight -= 1
                        self._latencies.append(time.monotonic() - started)
        finally:
            # Cancelled or failed while still waiting on a semaphore: the
            # decrement inside never ran, so undo the increment here. Without
            # this the waiting count leaks and every later request for that
            # student gets a spurious 429 once the leak reaches the limit.
            if not admitted:
                self._waiting[student_id] -= 1

    # ---------------------------------------------------------------- metrics
    @staticmethod
    def _pct(values: deque[float], q: float) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        idx = min(len(ordered) - 1, int(q * len(ordered)))
        return round(ordered[idx], 3)

    def stats(self) -> dict:
        waiting = {k: v for k, v in self._waiting.items() if v > 0}
        return {
            "capacity": {
                "max_concurrency": self.max_concurrency,
                "per_student_inflight": self.per_student_inflight,
                "per_student_queue": self.per_student_queue,
            },
            "now": {
                "in_flight": self.in_flight,
                "waiting_total": sum(waiting.values()),
                "waiting_by_student": waiting,
                "students_seen": len(self.per_student),
            },
            "totals": {
                "served": self.served,
                "errors": self.errors,
                "rejected_queue_full": self.rejected_queue_full,
            },
            "latency_seconds": {
                "upstream_p50": self._pct(self._latencies, 0.50),
                "upstream_p95": self._pct(self._latencies, 0.95),
                "queue_wait_p50": self._pct(self._waits, 0.50),
                "queue_wait_p95": self._pct(self._waits, 0.95),
            },
            "by_model": dict(sorted(self.per_model.items(), key=lambda kv: -kv[1])),
            "by_student": dict(sorted(self.per_student.items(), key=lambda kv: -kv[1])),
        }
