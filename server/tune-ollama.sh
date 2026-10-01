#!/usr/bin/env bash
# =============================================================================
#  Write Ollama's systemd drop-in correctly.
#
#      sudo ./tune-ollama.sh
#
#  Does NOT restart Ollama -- a restart drops in-flight requests, so you choose
#  when. It prints the command afterwards.
#
#  Override any value by exporting it first:
#      MAX_LOADED=3 sudo -E ./tune-ollama.sh
# =============================================================================
set -euo pipefail

DIR=/etc/systemd/system/ollama.service.d
CONF="$DIR/override.conf"

MAX_LOADED="${MAX_LOADED:-2}"
KEEP_ALIVE="${KEEP_ALIVE:-30m}"
NUM_PARALLEL="${NUM_PARALLEL:-2}"
# Empty BIND_LOOPBACK=0 leaves OLLAMA_HOST alone, for a box where something
# still talks to :11434 directly.
BIND_LOOPBACK="${BIND_LOOPBACK:-1}"

say()  { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
ok()   { printf '\033[32m    ok  %s\033[0m\n' "$*"; }
warn() { printf '\033[33m    !!  %s\033[0m\n' "$*"; }
die()  { printf '\033[31m    !!  %s\033[0m\n' "$*"; exit 1; }

[ "$(id -u)" -eq 0 ] || die "run with sudo"
command -v systemctl >/dev/null 2>&1 || die "no systemd here"
systemctl list-unit-files ollama.service >/dev/null 2>&1 || warn "no ollama.service found; writing the drop-in anyway"

say "Writing $CONF"
mkdir -p "$DIR"
[ -f "$CONF" ] && cp "$CONF" "$CONF.bak.$(date +%Y%m%d%H%M%S)" && ok "existing file backed up"

{
  echo "# Written by tune-ollama.sh. The [Service] header is required, and a"
  echo "# commented-out Environment= line does nothing -- both are easy to get"
  echo "# wrong by hand, which is why this script exists."
  echo "[Service]"
  echo "Environment=\"OLLAMA_MAX_LOADED_MODELS=$MAX_LOADED\""
  echo "Environment=\"OLLAMA_KEEP_ALIVE=$KEEP_ALIVE\""
  echo "Environment=\"OLLAMA_NUM_PARALLEL=$NUM_PARALLEL\""
  if [ "$BIND_LOOPBACK" = "1" ]; then
    echo "Environment=\"OLLAMA_HOST=127.0.0.1:11434\""
  fi
} > "$CONF"
chmod 644 "$CONF"
sed 's/^/    /' "$CONF"

say "Validating"
systemctl daemon-reload
if systemd-analyze verify ollama.service 2>&1 | grep -qi "ollama.service.d"; then
  systemd-analyze verify ollama.service 2>&1 | sed 's/^/    /'
  die "systemd rejected the drop-in; the file is above and a .bak is beside it"
fi
ok "drop-in parses"

say "Effective configuration (after restart)"
systemctl cat ollama 2>/dev/null | sed -n '/override.conf/,$p' | sed 's/^/    /' || true

cat <<ENDDONE

================================================================================
 Written, not yet applied. Restart when nobody is mid-request:

   sudo systemctl restart ollama
   systemctl show ollama -p Environment      # all values should appear
   ollama ps                                 # what is resident, and its VRAM

 BIND_LOOPBACK=1 was used, so Ollama will listen on 127.0.0.1 only and the
 gateway becomes the sole exposed listener. Anything still hitting :11434
 directly will stop working. Re-run with BIND_LOOPBACK=0 to leave it open.
================================================================================
ENDDONE
