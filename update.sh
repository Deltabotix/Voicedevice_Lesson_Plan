#!/usr/bin/env bash
# Pull the latest lessons from GitHub (run from inside your clone).
#
# Keeps student edits in **/my_program.py and updates everything else to match
# origin (run, reset, helpers, guides, …).
#
#   ./update.sh
#   ./update.sh --pull-only   # old behaviour: git pull --ff-only (may fail on conflicts)
set -euo pipefail

LESSONS_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$LESSONS_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Error: ~/lessons is not a git clone. Clone the lessons repo first." >&2
    exit 1
fi

MODE="${1:-sync}"

log() { echo "[update] $*"; }

ensure_executable() {
    local f
    for f in run reset update.sh run.sh; do
        [[ -f "$f" ]] && chmod +x "$f"
    done
}

echo "Fetching updates…"
git fetch --tags origin

branch="$(git rev-parse --abbrev-ref HEAD)"
remote="origin/$branch"

if ! git rev-parse --verify "$remote" >/dev/null 2>&1; then
    echo "Error: $remote not found after fetch." >&2
    exit 1
fi

if [[ "$MODE" == "--pull-only" ]]; then
    log "Pulling $branch (ff-only)…"
    git pull --ff-only origin "$branch"
    ensure_executable
    log "Done. Current commit: $(git rev-parse --short HEAD)"
    exit 0
fi

# Stash student work (only my_program.py in any lesson folder).
STASHED=0
if git stash push -m "voicedevice-lessons-update" -- '**/my_program.py' >/dev/null 2>&1; then
    STASHED=1
    log "Saved local my_program.py edits."
fi

log "Syncing lesson kit files from $remote …"
git reset --hard "$remote"

if [[ "$STASHED" == 1 ]]; then
    if git stash pop >/dev/null 2>&1; then
        log "Restored your my_program.py edits."
    else
        log "Warning: could not restore my_program.py automatically."
        log "  Your edits may be in: git stash list"
        log "  Restore with: git stash pop"
    fi
fi

ensure_executable

log "Done. Current commit: $(git rev-parse --short HEAD)"
log "Note: voicekit venv at /opt/voicedevice/voicekit_v2/venv is unchanged."
