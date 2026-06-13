#!/usr/bin/env bash
# First-time setup on the Pi after cloning ~/lessons.
set -euo pipefail

LESSONS_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$LESSONS_DIR"

if [[ ! -d venv ]]; then
    echo "Creating venv …"
    python3 -m venv venv
fi

echo "Installing packages …"
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo "Done. Try: ./run 1"
