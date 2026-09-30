#!/usr/bin/env bash
# Start the gateway. Creates .venv and installs deps on first run.
#   ./run.sh                   # foreground, port 8080
#   PORT=9000 ./run.sh         # different port
#   ./run.sh --install-only    # build the venv and exit (image build, or
#                              #   install-service.sh priming it as the right user)
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

INSTALL_ONLY=0
[ "${1:-}" = "--install-only" ] && INSTALL_ONLY=1

PORT="${PORT:-8080}"

# Install only when needed. Under systemd with Restart=always a crash loop would
# otherwise hit the network on every restart, and a pip failure would turn a
# recoverable crash into an unrecoverable one.
STAMP=".venv/.deps-installed"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
if [ ! -f "$STAMP" ] || [ requirements.txt -nt "$STAMP" ]; then
  ./.venv/bin/pip install -q --upgrade pip
  ./.venv/bin/pip install -q -r requirements.txt
  touch "$STAMP"
fi

if [ "$INSTALL_ONLY" -eq 1 ]; then
  echo "dependencies ready in .venv; not starting the server"
  exit 0
fi

echo "gateway  -> http://0.0.0.0:${PORT}"
echo "upstream -> ${OLLAMA_URL:-http://127.0.0.1:11434}"
echo "students set  LLM_BASE_URL=http://<this box>:${PORT}"
echo
# --workers 1 is required, not a default: the queue lives in process memory, so a
#   second worker would be a second independent queue.
# --no-proxy-headers is also required. uvicorn defaults proxy_headers=True, which
#   makes IT rewrite request.client from X-Forwarded-For before the gateway sees
#   the request -- so a client could pick its own identity and take unlimited
#   queue slots. With this off, request.client is the real TCP peer and
#   TRUST_FORWARDED_FOR (default off) is the only thing that can change that.
exec ./.venv/bin/uvicorn aicyber_gateway.app:app \
    --host 0.0.0.0 --port "$PORT" \
    --workers 1 \
    --no-proxy-headers \
    --log-level info
