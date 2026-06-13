#!/usr/bin/env bash
# Pull the latest lessons from GitHub (run from inside your clone).
set -euo pipefail

LESSONS_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$LESSONS_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Error: ~/lessons is not a git clone. Clone the lessons repo first." >&2
    exit 1
fi

echo "Fetching updates…"
git fetch --tags origin

branch="$(git rev-parse --abbrev-ref HEAD)"
echo "Pulling $branch …"
git pull --ff-only origin "$branch"

echo "Done. Current commit: $(git rev-parse --short HEAD)"
echo "Note: voicekit venv at /opt/voicedevice/voicekit_v2/venv is unchanged."
