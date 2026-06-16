#!/usr/bin/env bash
# Factory / image build ONLY — passwordless systemctl for lessons ./run script.
# Run once as root during image build (after lessons are copied to the image):
#   sudo ./image_setup_sudoers.sh
set -euo pipefail

LESSONS_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$LESSONS_DIR/voicedevice-captiveportal.sudoers"
DEST="/etc/sudoers.d/voicedevice-captiveportal"

if [[ "$(id -u)" -ne 0 ]]; then
    echo "Run as root: sudo $0" >&2
    exit 1
fi

if [[ ! -f "$SRC" ]]; then
    echo "Error: missing $SRC" >&2
    exit 1
fi

install -m 440 "$SRC" "$DEST"
visudo -cf "$DEST"
echo "Installed $DEST — ./run can stop/start captiveportal.service without a password."
