#!/usr/bin/env bash
# =============================================================================
#  AI for Cybersecurity -- Introductory Certification
#  One-time setup for a cyber-range student VM.
#
#  Run it from the repository root:   ./setup.sh
#  Re-running it is safe.
# =============================================================================
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$REPO/.venv"
KERNEL_NAME="aicyber"
KERNEL_LABEL="Python (AI-Cyber)"

say()  { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[33m    !! %s\033[0m\n' "$*"; }
ok()   { printf '\033[32m    ok  %s\033[0m\n' "$*"; }

# --- 1. interpreter ----------------------------------------------------------
# TensorFlow publishes wheels for a narrow band of Python versions. Picking an
# unsupported interpreter fails three minutes later inside pip with a wall of
# resolver output that says nothing useful, so refuse it up front instead.
say "Finding a supported Python"
SUPPORTED="3.11 3.12 3.13"

py_version() { "$1" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null; }
is_supported() { case " $SUPPORTED " in *" $1 "*) return 0 ;; *) return 1 ;; esac; }

PY=""
# an explicit PYTHON= wins, but is still checked
if [ -n "${PYTHON:-}" ]; then
  V="$(py_version "$PYTHON")"
  if is_supported "$V"; then PY="$PYTHON"
  else warn "PYTHON=$PYTHON is Python ${V:-unknown}, which this course does not support."; fi
fi
# otherwise take the newest supported interpreter on PATH
if [ -z "$PY" ]; then
  for cand in python3.13 python3.12 python3.11 python3; do
    command -v "$cand" >/dev/null 2>&1 || continue
    V="$(py_version "$cand")"
    if is_supported "$V"; then PY="$cand"; break; fi
  done
fi

if [ -z "$PY" ]; then
  warn "No supported Python found on PATH."
  warn "This course needs Python 3.11, 3.12 or 3.13 -- TensorFlow publishes no"
  warn "wheels outside that range, so the install cannot succeed without one."
  if command -v python3 >/dev/null 2>&1; then
    warn "The python3 on your PATH is $(py_version python3)."
  fi
  warn ""
  warn "Install one, then re-run. On Debian/Ubuntu:  sudo apt install python3.12 python3.12-venv"
  warn "Or point this script at an existing one:     PYTHON=/usr/bin/python3.12 ./setup.sh"
  exit 1
fi
ok "using $PY (Python $(py_version "$PY"))"

# --- 2. virtual environment --------------------------------------------------
say "Creating the virtual environment at .venv"
if [ -d "$VENV" ]; then
  ok ".venv already exists -- reusing it"
else
  "$PY" -m venv "$VENV"
  ok "created"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install --upgrade pip --quiet
ok "pip $(pip --version | awk '{print $2}')"

# --- 3. dependencies ---------------------------------------------------------
say "Installing course dependencies (this pulls ~500 MB and takes a few minutes)"
if [ -f "$REPO/requirements.lock" ]; then
  pip install -r "$REPO/requirements.lock"
  ok "installed from requirements.lock (pinned)"
else
  pip install -r "$REPO/requirements.txt"
  ok "installed from requirements.txt"
fi

# --- 4. Jupyter kernel -------------------------------------------------------
say "Registering the Jupyter kernel"
python -m ipykernel install --user --name "$KERNEL_NAME" --display-name "$KERNEL_LABEL" >/dev/null
ok "kernel '$KERNEL_LABEL' registered -- pick it in VS Code's kernel selector"

# --- 5. model-server credentials --------------------------------------------
say "Setting up model-server access (Module 6 only)"
if [ -f "$REPO/.env" ]; then
  ok ".env already exists -- leaving it alone"
else
  cat > "$REPO/.env" <<'ENDENV'
# Module 6 talks to the course model server over HTTP. Both values come from
# your instructor. This file is gitignored: the token must never reach a
# notebook cell, a screenshot or a commit. Module 6 Section 1.1 explains why
# at length -- and that section is the reason this file exists.
LLM_BASE_URL=http://192.168.1.10
LLM_API_KEY=replace-me-with-your-issued-token
ENDENV
  chmod 600 "$REPO/.env"
  ok "wrote .env (mode 600) -- put your issued token in it before Module 6"
fi

# --- 6. verification ---------------------------------------------------------
say "Verifying the stack"
python - <<'ENDCHECK'
import importlib, sys
mods = [("numpy",None),("pandas",None),("pyarrow",None),("scipy",None),
        ("sklearn",None),("imblearn",None),("matplotlib",None),("seaborn",None),
        ("tensorflow",None),("requests",None),("shap",None),("dotenv",None)]
bad = []
for name,_ in mods:
    try:
        m = importlib.import_module(name)
        print(f"    ok  {name:<14}{getattr(m,'__version__','(no __version__)')}")
    except Exception as e:
        bad.append(name); print(f"    !!  {name:<14}FAILED: {type(e).__name__}")
import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
print(f"\n    TensorFlow sees {len(gpus)} GPU(s) -- CPU-only is expected on these VMs.")
if bad:
    print(f"\n    {len(bad)} package(s) failed to import: {', '.join(bad)}")
    sys.exit(1)
ENDCHECK

say "Checking the course datasets are reachable"
python - <<'ENDDATA'
import urllib.request, sys
URL = ("https://github.com/abramweigant/AI-Cyber-Intro-Cert/raw/refs/heads/main/"
       "forensic_log_truth.csv")
try:
    with urllib.request.urlopen(URL, timeout=20) as r:
        r.read(64)
    print("    ok  datasets reachable over HTTPS")
except Exception as e:
    print(f"    !!  could not reach the dataset host: {type(e).__name__}: {e}")
    print("        Every module loads data through DATA_URL. Tell your instructor")
    print("        if this fails -- it means the VM has no egress to github.com.")
    sys.exit(1)
ENDDATA

cat <<ENDDONE

================================================================================
 Setup complete.

 In VS Code:
   1. Open this folder.
   2. Open Module1_Student.ipynb.
   3. Kernel selector (top right) -> "$KERNEL_LABEL".

 Before Module 6, put your issued token in .env (LLM_API_KEY).
 Everything else runs offline of the model server.
================================================================================
ENDDONE
