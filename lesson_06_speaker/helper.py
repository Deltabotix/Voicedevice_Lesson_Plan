from __future__ import annotations

import shutil
import struct
import subprocess
import sys
import wave
from pathlib import Path

_LESSON_DIR = Path(__file__).resolve().parent

_TEST_SOUND_CANDIDATES = (
    _LESSON_DIR / "test.wav",
    Path("/usr/share/sounds/alsa/Front_Left.wav"),
    Path("/usr/share/sounds/alsa/Front_Center.wav"),
    Path("/usr/share/sounds/alsa/Rear_Left.wav"),
)


def find_test_sound() -> Path:
    for path in _TEST_SOUND_CANDIDATES:
        if path.is_file():
            return path
    raise RuntimeError(
        "No test WAV found. Add test.wav to this lesson folder, "
        "or use a Pi image with /usr/share/sounds/alsa/*.wav"
    )


def play_sound(path: Path | str, device: str = "") -> None:
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    cmd = ["aplay", "-q"]
    dev = (device or "").strip()
    if dev:
        cmd.extend(["-D", dev])
    cmd.append(str(path))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"aplay failed: {err or 'unknown error'}")
    print(f"Playing {path.name}")


def try_play_sound(path: Path | str, device: str = "") -> bool:
    try:
        play_sound(path, device)
        return True
    except Exception:
        return False


def print_sound_help() -> None:
    lines = [
        "",
        "=== Speaker quick checklist ===",
        "1) Speaker wired to amp; headphones unplugged if using the kit speaker.",
        "2) Volume: alsamixer (not muted).",
        "3) List devices: aplay -l — try plughw:0,0 in AUDIO_DEVICE.",
        "4) Need aplay? (alsa-utils package on the Pi image.)",
        "5) This lesson uses WAV files. Add test.wav here if system demos are missing.",
        "",
    ]
    print("\n".join(lines), file=sys.stderr)


def cleanup() -> None:
    pass
