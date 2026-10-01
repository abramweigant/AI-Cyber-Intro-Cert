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

# Refuse to tune a unit that is already broken: a drop-in cannot fix a missing
# ExecStart=, and layering one on top makes the real fault harder to see.
PRE="$(systemd-analyze verify ollama.service 2>&1 || true)"
if printf '%s' "$PRE" | grep -qi "no ExecStart"; then
  printf '%s\n' "$PRE" | sed 's/^/    /'
  warn "The BASE unit /etc/systemd/system/ollama.service has no ExecStart=."
  warn "That is not something this drop-in can fix, and it is usually caused by"
  warn "'systemctl edit --full' saving a buffer of only comment lines."
  warn ""
  warn "If the distro shipped a unit, the /etc copy is just shadowing it:"
  warn "  ls -la /lib/systemd/system/ollama.service /usr/lib/systemd/system/ollama.service"
  warn "  sudo rm /etc/systemd/system/ollama.service && sudo systemctl daemon-reload"
  warn ""
  warn "Otherwise see the troubleshooting section of README.md for the unit to"
  warn "write back. Re-run this script once Ollama starts."
  die "refusing to tune a unit that cannot start"
fi

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

# Three checks, because each catches something the others miss.
PROBLEM=0

# 1. systemd's own parser. Flags "Assignment outside of section" and unknown
#    directives, with a file and line number.
VERIFY="$(systemd-analyze verify ollama.service 2>&1 || true)"
if printf '%s' "$VERIFY" | grep -qiE "lvalue|outside of section|Failed to parse|bad-setting"; then
  printf '%s\n' "$VERIFY" | sed 's/^/    /'
  PROBLEM=1
fi

# 2. Did the unit actually load? This is the check that matters: a rejected
#    drop-in leaves the unit in "bad-setting" and it will not start at all.
LOADSTATE="$(systemctl show ollama -p LoadState --value 2>/dev/null || echo unknown)"
if [ "$LOADSTATE" != "loaded" ]; then
  warn "LoadState=$LOADSTATE (expected 'loaded')"
  systemctl status ollama --no-pager 2>&1 | head -8 | sed 's/^/    /'
  PROBLEM=1
fi

# 3. Did our settings survive into the merged config?
ENVNOW="$(systemctl show ollama -p Environment --value 2>/dev/null || true)"
if ! printf '%s' "$ENVNOW" | grep -q "OLLAMA_MAX_LOADED_MODELS"; then
  warn "OLLAMA_MAX_LOADED_MODELS is not in the merged Environment yet"
  warn "  (expected before restart on some systemd versions -- not fatal)"
fi

if [ "$PROBLEM" -eq 1 ]; then
  echo
  warn "systemd is unhappy with the unit. The file written is shown above and the"
  warn "previous one is beside it as override.conf.bak.*"
  warn "To back the change out entirely:"
  warn "  sudo rm $CONF && sudo systemctl daemon-reload"
  die "aborting before telling you to restart something that will not start"
fi
ok "drop-in parses and the unit loads"

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
