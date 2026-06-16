#!/usr/bin/env bash
# Launcher for lessons — same as ./run (this file exists for students who expect .sh).
# Note: ~/run.sh on the kit is different — it starts voicekit, not lessons.
exec "$(cd "$(dirname "$0")" && pwd)/run" "$@"
