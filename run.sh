#!/usr/bin/env bash
# Same as ./run — use either name from the lessons folder.
exec "$(cd "$(dirname "$0")" && pwd)/run" "$@"
