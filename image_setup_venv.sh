#!/usr/bin/env bash
# Factory / image build ONLY — add lesson-only packages into voicekit_v2 venv.
# Students do NOT run this. The kit uses /opt/voicedevice/voicekit_v2/venv.
#
# On the Pi during image build:
#   cd ~/lessons && ./image_setup_venv.sh
set -euo pipefail

LESSONS_DIR="$(cd "$(dirname "$0")" && pwd)"
VOICEKIT_VENV="${LESSONS_VENV:-/opt/voicedevice/voicekit_v2/venv}"
PY="$VOICEKIT_VENV/bin/python3"

if [[ ! -x "$PY" ]]; then
    echo "Error: voicekit venv not found at $VOICEKIT_VENV" >&2
    echo "  Set LESSONS_VENV=/path/to/venv if your image uses a different path." >&2
    exit 1
fi

if [[ ! -f "$LESSONS_DIR/requirements.txt" ]]; then
    echo "Error: requirements.txt not found in $LESSONS_DIR" >&2
    exit 1
fi

echo "Using voicekit venv: $VOICEKIT_VENV"
echo "Installing lesson extras …"
"$PY" -m pip install --upgrade pip
"$PY" -m pip install -r "$LESSONS_DIR/requirements.txt"

echo "Done. Lessons will use: $PY"
