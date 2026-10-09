#!/usr/bin/env bash
# =============================================================================
#  Pull every model Module 6 uses onto the GPU box.
#
#  Run it on the GPU box after cloning this repo:
#      cd AI-Cyber-Intro-Cert/server && ./provision_models.sh
#
#  Safe to re-run: Ollama skips layers it already has.
# =============================================================================
set -uo pipefail

# --- the model set -----------------------------------------------------------
# Ordered smallest-first, so a disk or network problem shows up on a 2 GB pull
# rather than a 17 GB one.
#
# These are Ollama-registry tags, which is what Module 6's setup cell declares
# and what its connectivity check asserts by exact string. To source a model
# from Hugging Face instead, swap the tag for an hf.co reference, e.g.
#
#     "hf.co/bartowski/Qwen3-8B-GGUF:Q4_K_M|workhorse -- Section 2"
#
# and change the matching constant in Module 6's setup cell (WORKHORSE,
# CAPSTONE, REASONER, SMALL, MEDIUM) to the same string, or the connectivity
# check will report the model as missing.
MODELS=(
  "llama3.2:3b|Section 3 prompt injection -- the model that folds   (~2.0 GB)"
  "qwen3:8b|WORKHORSE -- Section 2 classification labs              (~5.2 GB)"
  "phi4:latest|Section 3 prompt injection -- middle of the range    (~9.1 GB)"
  "gpt-oss:20b|CAPSTONE S5 log triage, S4 XAI, S3 largest model    (~13 GB)"
)
# gemma3:27b is deliberately absent: 17 GB does not fit the range's 16 GB vGPU
# (GRID A100D-16C), so it ran on partial CPU offload. gpt-oss:20b took over as
# the capstone model. If you re-add it, raise NEED_GB and expect swapping.
NEED_GB=35            # ~29 GB of models plus working room

say()  { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
ok()   { printf '\033[32m    ok  %s\033[0m\n' "$*"; }
warn() { printf '\033[33m    !!  %s\033[0m\n' "$*"; }

# --- 1. find ollama ----------------------------------------------------------
say "Locating Ollama"
OLLAMA=""
if command -v ollama >/dev/null 2>&1; then
  OLLAMA="ollama"
  ok "native: $(ollama --version 2>/dev/null | head -1)"
elif command -v docker >/dev/null 2>&1; then
  CID="$(docker ps --filter ancestor=ollama/ollama --format '{{.Names}}' | head -1)"
  [ -z "$CID" ] && CID="$(docker ps --format '{{.Names}}' | grep -i ollama | head -1)"
  if [ -n "$CID" ]; then
    OLLAMA="docker exec $CID ollama"
    ok "container: $CID"
  fi
fi
if [ -z "$OLLAMA" ]; then
  warn "Ollama not found, natively or as a running container."
  warn "Install it (https://ollama.com/download) or start the container, then re-run."
  exit 1
fi

# --- 2. disk ------------------------------------------------------------------
say "Checking disk"
AVAIL_GB="$(df -Pk "${HOME}" 2>/dev/null | awk 'NR==2 {printf "%d", $4/1048576}')"
if [ -n "${AVAIL_GB:-}" ] && [ "$AVAIL_GB" -gt 0 ]; then
  if [ "$AVAIL_GB" -lt "$NEED_GB" ]; then
    warn "only ${AVAIL_GB} GB free; the full set needs about ${NEED_GB} GB."
    warn "Pulling anyway -- it will fail partway if it runs out."
  else
    ok "${AVAIL_GB} GB free (need ~${NEED_GB} GB)"
  fi
else
  warn "could not determine free space; continuing"
fi

# --- 3. pull ------------------------------------------------------------------
say "Pulling ${#MODELS[@]} models"
FAILED=()
for entry in "${MODELS[@]}"; do
  tag="${entry%%|*}"
  desc="${entry#*|}"
  printf '\n  --- %s\n      %s\n' "$tag" "$desc"
  if $OLLAMA pull "$tag"; then
    ok "$tag"
  else
    warn "FAILED: $tag"
    FAILED+=("$tag")
  fi
done

# --- 4. verify ----------------------------------------------------------------
# Exact-tag verification, because Module 6 checks membership by exact string.
say "Verifying every tag is present"
PRESENT="$($OLLAMA list 2>/dev/null | awk 'NR>1 {print $1}')"
MISSING=()
for entry in "${MODELS[@]}"; do
  tag="${entry%%|*}"
  if printf '%s\n' "$PRESENT" | grep -qx -- "$tag"; then
    ok "$tag"
  else
    warn "MISSING: $tag"
    MISSING+=("$tag")
  fi
done

say "Installed models"
$OLLAMA list

# Where models land depends on which user the service runs as, and a reinstall can
# change that -- the official installer creates an 'ollama' user reading
# /usr/share/ollama/.ollama, while a manually started server reads $HOME/.ollama.
# When they disagree, `ollama list` comes back empty and it looks like the models
# vanished. Surface the mismatch here instead.
say "Where the models actually live"
SVC_USER="$(systemctl show ollama -p User --value 2>/dev/null || true)"
[ -z "$SVC_USER" ] && SVC_USER="(not a systemd service)"
echo "    service runs as : $SVC_USER"
EXPLICIT="$(systemctl show ollama -p Environment --value 2>/dev/null | tr ' ' '\n' | grep '^OLLAMA_MODELS=' || true)"
[ -n "$EXPLICIT" ] && echo "    OLLAMA_MODELS   : ${EXPLICIT#OLLAMA_MODELS=}"
for d in /usr/share/ollama/.ollama/models "$HOME/.ollama/models" /var/lib/ollama/.ollama/models; do
  if [ -d "$d" ]; then
    sz="$(du -sh "$d" 2>/dev/null | cut -f1)"
    n="$(find "$d/manifests" -type f 2>/dev/null | wc -l | tr -d ' ')"
    echo "    $d  ->  ${sz:-?} , $n manifest(s)"
  fi
done
cat <<'ENDLOC'

    If a directory above holds your models but `ollama list` is empty, the
    service is reading a different one. Move them to the directory the service
    user owns rather than widening permissions on a home directory:

      sudo systemctl stop ollama
      sudo mkdir -p /usr/share/ollama/.ollama/models
      sudo mv "$HOME"/.ollama/models/* /usr/share/ollama/.ollama/models/
      sudo chown -R ollama:ollama /usr/share/ollama/.ollama
      sudo systemctl start ollama
ENDLOC

# --- 5. service tuning --------------------------------------------------------
say "Service tuning (apply these, then restart Ollama)"
cat <<'ENDTUNE'
    Ollama keeps one model loaded and unloads it after 5 minutes by default.
    Module 6 touches five models in one notebook run, so without this every
    switch is a reload from disk.

      sudo systemctl edit ollama

    [Service]
    Environment="OLLAMA_HOST=127.0.0.1:11434"    # gateway is the only listener
    Environment="OLLAMA_MAX_LOADED_MODELS=2"     # raise if VRAM allows
    Environment="OLLAMA_NUM_PARALLEL=2"
    Environment="OLLAMA_KEEP_ALIVE=30m"

      sudo systemctl restart ollama

    Bind Ollama to loopback and let the gateway be the only thing exposed:
    Ollama has no authentication, so anything that can reach 11434 can use it.
ENDTUNE

# --- 6. result ----------------------------------------------------------------
if [ ${#FAILED[@]} -eq 0 ] && [ ${#MISSING[@]} -eq 0 ]; then
  say "All ${#MODELS[@]} models present. Start the gateway next (see README.md)."
  exit 0
fi
say "Finished with problems"
[ ${#FAILED[@]}  -gt 0 ] && warn "pull failed:  ${FAILED[*]}"
[ ${#MISSING[@]} -gt 0 ] && warn "not present:  ${MISSING[*]}"
warn "Module 6's connectivity cell will name these as missing to students."
exit 1
