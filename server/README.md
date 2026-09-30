# AI-Cyber Gateway

Sits on the course GPU box between the student VMs and Ollama. It does three
things Ollama will not do for you:

1. **Authenticates** per-student bearer tokens. Ollama has no authentication of
   any kind — it answers anything that can reach its port. This gateway is the
   only control, which is the point Module 6 Section 1.1 now teaches.
2. **Queues fairly.** One request in flight per student, round-robin between
   students, bounded global concurrency. One student running Section 3's ~75
   calls cannot take the class's GPU for the duration.
3. **Scopes access** to the five course models, so nobody reaches a model the
   course has not budgeted for.

It speaks the two paths Module 6 uses — `GET /v1/models` and
`POST /v1/chat/completions` — so the notebook needs no changes beyond pointing
`LLM_BASE_URL` at this service.

---

## Install on the GPU box

```bash
# 1. models
git clone https://github.com/abramweigant/AI-Cyber-Intro-Cert.git
cd AI-Cyber-Intro-Cert/server
./provision_models.sh                       # pulls all five, verifies each tag

# 2. the gateway itself
sudo mkdir -p /opt/aicyber-gateway /etc/aicyber-gateway
sudo cp -r aicyber_gateway requirements.txt issue_token.py /opt/aicyber-gateway/
sudo useradd --system --home /opt/aicyber-gateway aicyber || true
cd /opt/aicyber-gateway
sudo python3 -m venv .venv
sudo .venv/bin/pip install -r requirements.txt

# 3. configuration
sudo cp /path/to/server/.env.example /etc/aicyber-gateway/gateway.env
sudo python3 -c "import secrets;print('ADMIN_TOKEN='+secrets.token_urlsafe(24))"
sudo nano /etc/aicyber-gateway/gateway.env      # set ADMIN_TOKEN, tune concurrency

# 4. student tokens
sudo TOKENS_FILE=/etc/aicyber-gateway/tokens.json \
     /opt/aicyber-gateway/.venv/bin/python /opt/aicyber-gateway/issue_token.py \
     mint --count 20 --prefix student
# ^ prints each token ONCE. Hand each student only their own line.

sudo chown -R aicyber:aicyber /opt/aicyber-gateway /etc/aicyber-gateway

# 5. service
sudo cp /path/to/server/aicyber-gateway.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now aicyber-gateway
curl -s localhost:8080/healthz
```

Then **bind Ollama to loopback** so the gateway is the only exposed listener:

```bash
sudo systemctl edit ollama
# [Service]
# Environment="OLLAMA_HOST=127.0.0.1:11434"
# Environment="OLLAMA_MAX_LOADED_MODELS=2"
# Environment="OLLAMA_NUM_PARALLEL=2"
# Environment="OLLAMA_KEEP_ALIVE=30m"
sudo systemctl restart ollama
```

Students put the gateway's address and their token in `.env` on their VM:

```
LLM_BASE_URL=http://192.168.1.10:8080
LLM_API_KEY=<their issued token>
```

---

## Operating it

```bash
# who is using it, how deep is the queue, how slow is it
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" localhost:8080/admin/stats | python3 -m json.tool

# token admin -- no restart needed, the file is watched
./issue_token.py list
./issue_token.py rotate student07        # student lost theirs
./issue_token.py revoke student12        # student left the cohort
```

**Tuning `MAX_CONCURRENCY`.** Start at 2 and watch `latency_seconds.queue_wait_p95`
in `/admin/stats`. Raise it only if queue wait is high *and* the GPU still has
VRAM headroom — three course models are 13–17 GB, so two resident at once is
already ~30 GB. If you raise it past what fits, Ollama starts swapping models
from disk and everyone gets slower.

### Two things not to change without understanding them

- **`--workers 1` in the systemd unit is load-bearing.** The scheduler's state
  is in-process: semaphores and counters live in one Python process. Two workers
  means two independent schedulers, so `MAX_CONCURRENCY=2` silently becomes 4 and
  the per-student fairness guarantee is gone. If you ever need more throughput,
  raise `MAX_CONCURRENCY`, not the worker count.
- **A bad token must return 401, not 403.** Module 6's `discover_endpoint()` keys
  its "your token was rejected, check `.env`" message off that exact status, and
  retries everything else. Returning 403 sends students chasing the wrong problem.

---

## Layout

| file | what it is |
|---|---|
| `aicyber_gateway/app.py` | FastAPI app: routes, validation, logging |
| `aicyber_gateway/scheduler.py` | the fairness policy — read the module docstring, the design is three sentences |
| `aicyber_gateway/auth.py` | token store; SHA-256 hashes only, hot-reloads on file change |
| `aicyber_gateway/upstream.py` | async Ollama client |
| `aicyber_gateway/config.py` | all settings, from the environment |
| `issue_token.py` | mint / list / revoke / rotate / remove |
| `provision_models.sh` | pull and verify the five course models |
| `aicyber-gateway.service` | systemd unit, with hardening |
| `tests/test_gateway.py` | 17 tests, no network required |

## Tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -q
```

The upstream is faked, so these run anywhere. Three are worth knowing about:
`test_bad_token_is_401_not_403` pins the contract above;
`test_one_student_cannot_starve_another` is the fairness policy;
`test_cancelled_while_queued_does_not_leak_waiting_count` covers a real leak
found during the build, where cancelling a queued request left the waiting
counter incremented and that student eventually got a permanent spurious 429.

## Security notes

- Tokens are stored as SHA-256 hashes. The plaintext is shown once at mint time
  and cannot be recovered — rotate instead. A credential store you can read back
  is not one, and Module 6 tells students to expect this.
- `tokens.json` is written mode 600 and is gitignored.
- The service unit runs as a dedicated non-login user with `ProtectSystem=strict`,
  `NoNewPrivileges`, and `/etc/aicyber-gateway` read-only.
- This is HTTP, not HTTPS. That is a deliberate call for an internal-only range
  with a bare IP: Let's Encrypt cannot issue for an IP, and a self-signed cert
  would make `requests` reject the connection inside the notebook's `chat()`.
  If the box ever becomes reachable from outside the range, put TLS in front of
  it before that happens.
