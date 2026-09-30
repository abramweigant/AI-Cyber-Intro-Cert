#!/usr/bin/env bash
# Start the gateway. Creates .venv and installs deps on first run.
#   ./run.sh                 # foreground, port 8080
#   PORT=9000 ./run.sh       # different port
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

PORT="${PORT:-8080}"
[ -d .venv ] || python3 -m venv .venv
./.venv/bin/pip install -q --upgrade pip
./.venv/bin/pip install -q -r requirements.txt

echo "gateway  -> http://0.0.0.0:${PORT}"
echo "upstream -> ${OLLAMA_URL:-http://127.0.0.1:11434}"
echo "students set  LLM_BASE_URL=http://<this box>:${PORT}"
echo
# One worker is required, not a default: the queue lives in process memory, so a
# second worker would be a second independent queue.
exec ./.venv/bin/uvicorn aicyber_gateway.app:app \
    --host 0.0.0.0 --port "$PORT" --workers 1 --log-level info
