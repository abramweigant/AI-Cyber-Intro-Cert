# AI-Cyber Gateway

A fair queue in front of Ollama on the course GPU box. It exists for one reason:
~20 students hitting one GPU directly will swamp it, and Ollama has no queueing
of its own.

**There is no authentication.** Anything on the range that can reach this port
may use it. That is deliberate, and Module 6 Section 1.1 teaches students exactly
that — what an unauthenticated inference service means, and what you would do
about it if this box were reachable from anywhere else.

Clients are identified by IP, so each student VM gets a fair share with no
registration, no tokens and nothing to hand out.

## Run it

```bash
git clone https://github.com/abramweigant/AI-Cyber-Intro-Cert.git
cd AI-Cyber-Intro-Cert/server

./provision_models.sh     # pull the five course models, verify each tag
./run.sh                  # creates .venv on first run, then serves on :8080
```

That's it. Students point at it:

```
LLM_BASE_URL=http://192.168.1.10:8080
```

To keep it running across reboots, edit the two paths in
`aicyber-gateway.service` and install it — instructions are in the file.

## Tune it

```bash
curl -s localhost:8080/stats | python3 -m json.tool
```

Watch `latency_seconds.queue_wait_p95`. If students are waiting and the GPU still
has VRAM headroom, raise concurrency:

```bash
MAX_CONCURRENCY=3 ./run.sh
```

Two of the course models resident at once is already ~30 GB, so past that Ollama
starts swapping from disk and everyone gets slower. `by_client` in `/stats` shows
which VM is queueing, which is usually the question you actually have.

| setting | default | what it does |
|---|---|---|
| `OLLAMA_URL` | `http://127.0.0.1:11434` | upstream |
| `MAX_CONCURRENCY` | 2 | requests executing against Ollama at once |
| `PER_CLIENT_INFLIGHT` | 1 | per VM; raising this breaks fairness |
| `PER_CLIENT_QUEUE` | 8 | per VM, then 429 |
| `ALLOWED_MODELS` | the five course models | refuses anything else |
| `MAX_TOKENS_CAP` | 4096 | caps output length |
| `PORT` | 8080 | listen port |

Also worth setting on Ollama itself, so it stops unloading models between calls:

```bash
sudo systemctl edit ollama
# [Service]
# Environment="OLLAMA_MAX_LOADED_MODELS=2"
# Environment="OLLAMA_KEEP_ALIVE=30m"
sudo systemctl restart ollama
```

## Two things not to change casually

- **`--workers 1`.** The queue is in process memory. Two workers means two
  independent queues, so `MAX_CONCURRENCY=2` silently becomes 4 and the fairness
  guarantee is gone. Raise `MAX_CONCURRENCY` instead.
- **The `ALLOWED_MODELS` list.** It is not a security control; it stops one
  student invoking `llama4:scout` at ~5–15 tok/s and wrecking throughput for the
  class. Keep it in step with Module 6's setup cell.

## Layout

| file | what it is |
|---|---|
| `aicyber_gateway/scheduler.py` | the fairness policy — the docstring explains it in three sentences |
| `aicyber_gateway/app.py` | routes and validation |
| `aicyber_gateway/upstream.py` | async Ollama client |
| `aicyber_gateway/config.py` | settings, from the environment |
| `provision_models.sh` | pull and verify the five models |
| `run.sh` | start it |
| `tests/test_gateway.py` | 13 tests, no network needed |

```bash
./.venv/bin/python -m pytest tests/ -q
```
