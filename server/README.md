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

./provision_models.sh        # pull the five course models, verify each tag
sudo ./install-service.sh    # run it as a service, starting at boot
```

That's it. Students point at it:

```
LLM_BASE_URL=http://192.168.1.10:8080
```

**Use the service, not `./run.sh &`.** `run.sh` `exec`s uvicorn, so backgrounding
it over SSH means it takes the SIGHUP when you log out — and there is nothing to
restart it after a crash or a reboot. `install-service.sh` detects the directory
and the owning user, writes the unit, enables it at boot and checks `/healthz`.
Re-running it is how you change a setting:

```bash
MAX_CONCURRENCY=3 sudo -E ./install-service.sh
```

`./run.sh` in the foreground is still the right thing for testing, and
`./run.sh --install-only` just builds the venv (useful during an image build).

```bash
systemctl status aicyber-gateway
journalctl -u aicyber-gateway -f
```

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
| `ALLOWED_MODELS` | the five course models | refuses anything else; set **empty** to allow whatever Ollama serves |
| `TRUST_FORWARDED_FOR` | off | believe `X-Forwarded-For`. Only with a real proxy in front |
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

## Sharing the box with another course

Pulling and using the **same models** is completely fine — Ollama models are
content-addressed files, so two courses using `qwen3:8b` share one copy and
`ollama pull` is idempotent. Nothing to coordinate there.

Two things do need a decision:

### Checklist for a second course on this gateway

Fairness needs nothing: their VMs are just more client IPs, so per-client
round-robin covers both cohorts automatically. Four things to settle:

1. **Models.** Either add theirs to `ALLOWED_MODELS`, or set `ALLOWED_MODELS=`
   (empty) to pass through whatever Ollama serves. Empty is simpler; keeping a
   union list is better, because it is what stops anyone invoking
   `llama4:scout` at ~5–15 tok/s and wrecking throughput for **both** courses.
2. **`MAX_TOKENS_CAP`** (default 4096) applies to them too. Module 6 never wants
   more, but a course doing long generation or code will notice the clip. Raise
   it if so — it exists to stop one request holding a worker for minutes, not as
   a policy.
3. **Streaming** is supported: pass `stream: true` and it goes straight through
   as `text/event-stream`. The queue slot is held for the whole stream, which is
   correct — the GPU is busy that entire time. Module 6 never streams.
4. **`MAX_CONCURRENCY`** now serves both cohorts. The queue simply gets deeper,
   which is the right behaviour; fairness holds and latency rises. Watch
   `queue_wait_p95` before raising it, and read the VRAM note below first.

**And the one that will actually bite: VRAM.**

`OLLAMA_MAX_LOADED_MODELS` caps how many models stay resident. If the two courses
use *different* models and the sum does not fit, Ollama evicts and reloads on
every switch — a 13–17 GB read from disk each time. Everything gets slower for
everyone and it looks like the gateway is at fault.

Check what will be resident:

```bash
ollama ps          # what is loaded right now, and its VRAM footprint
nvidia-smi         # how much headroom is left
```

If the two sets do not fit together, either raise `OLLAMA_MAX_LOADED_MODELS` (if
VRAM allows), or agree to run the courses at different times, or agree on a
shared model set. For reference, one full Module 6 pass is **~390 requests**
(qwen3:8b 168, gemma3:27b 80, llama3.2:3b 70, phi4 70, gpt-oss:20b 1), so a
cohort of 20 is roughly 7,800.

This is the failure mode most likely to get blamed on the gateway. If both
courses report everything being slow, check `ollama ps` before touching
`MAX_CONCURRENCY`.

## Two things not to change casually

- **`--workers 1` and `--no-proxy-headers` in `run.sh`.** The first: the queue is
  in process memory, so two workers means two independent queues and
  `MAX_CONCURRENCY=2` silently becomes 4. The second is subtler — uvicorn defaults
  `proxy_headers=True`, which makes *uvicorn* rewrite `request.client` from
  `X-Forwarded-For` before the gateway sees the request. With that on, any client
  can pick its own identity and take unlimited queue slots. This was a real bug:
  the gateway gated the header correctly and the bypass still worked underneath.
  A test asserts both flags are still in `run.sh`. Only set
  `TRUST_FORWARDED_FOR=1` if a proxy you control is genuinely in front.
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
| `run.sh` | start it in the foreground; `--install-only` just builds the venv |
| `install-service.sh` | install it as a systemd service, paths detected |
| `tests/test_gateway.py` | 13 tests, no network needed |

```bash
./.venv/bin/python -m pytest tests/ -q
```
