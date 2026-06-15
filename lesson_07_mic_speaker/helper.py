from __future__ import annotations

import shutil
import struct
import subprocess
import sys
import wave
from pathlib import Path

_LESSON_DIR = Path(__file__).resolve().parent
CAPTURE_FILE = _LESSON_DIR / "capture.wav"

_REPLY_CANDIDATES = (
    _LESSON_DIR / "reply.wav",
    Path("/usr/share/sounds/alsa/Front_Center.wav"),
)


def check_audio_tools() -> None:
    for name in ("arecord", "aplay"):
        if shutil.which(name) is None:
            raise FileNotFoundError(
                f"Missing '{name}'. The kit image should include alsa-utils."
            )


def record(seconds: int, out_path: Path | None = None, input_device: str = "") -> Path:
    if seconds < 1 or seconds > 30:
        raise ValueError("Record 1–30 seconds for class demos.")
    path = Path(out_path or CAPTURE_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "arecord", "-q", "-f", "S16_LE", "-r", "16000", "-c", "1",
        "-d", str(int(seconds)), str(path),
    ]
    dev = (input_device or "").strip()
    if dev:
        cmd[1:1] = ["-D", dev]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=seconds + 30)
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"arecord failed: {err or 'unknown error'}")
    print(f"Recorded {seconds}s to {path.name}")
    return path


def loudness_level(wav_path: Path) -> float:
    wav_path = Path(wav_path)
    if not wav_path.is_file():
        raise ValueError(f"Not a file: {wav_path}")
    with wave.open(str(wav_path), "rb") as w:
        raw = w.readframes(w.getnframes())
        width = w.getsampwidth()
    if width != 2 or len(raw) < 2:
        return 0.0
    peak = 0
    for i in range(0, len(raw) - 1, 2):
        sample = struct.unpack_from("<h", raw, i)[0]
        peak = max(peak, abs(sample))
    level = min(1.0, peak / 32768.0)
    print(f"Loudness peak: {level:.2f} (0 = quiet, 1 = loud)")
    return level


def play_sound(path: Path | str, output_device: str = "") -> None:
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    cmd = ["aplay", "-q"]
    dev = (output_device or "").strip()
    if dev:
        cmd.extend(["-D", dev])
    cmd.append(str(path))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"aplay failed: {err or 'unknown error'}")
    print(f"Playing {path.name}")


def find_reply_sound() -> Path:
    for path in _REPLY_CANDIDATES:
        if path.is_file():
            return path
    raise RuntimeError("No reply.wav here and no system WAV fallback.")


def print_mic_help() -> None:
    lines = [
        "",
        "=== Mic + speaker checklist ===",
        "1) arecord -l and aplay -l — note card numbers for mic and speaker.",
        "2) Try empty INPUT_DEVICE / OUTPUT_DEVICE first, then plughw:CARD,DEV.",
        "3) Lower speaker volume to avoid feedback squeal.",
        "4) Speak during record — peak should not stay at 0.",
        "",
    ]
    print("\n".join(lines), file=sys.stderr)


def cleanup() -> None:
    pass
