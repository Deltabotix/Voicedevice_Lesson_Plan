#!/usr/bin/env bash
# Same as ./reset_lesson.sh — use either name from the lessons folder.
exec "$(cd "$(dirname "$0")" && pwd)/reset_lesson.sh" "$@"
