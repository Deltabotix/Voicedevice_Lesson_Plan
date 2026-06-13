"""
Lesson 5 challenge — Microphone + speaker (Module 5).
Record a short WAV with arecord, show a simple loudness idea, play it back with aplay.

Edit: INPUT_DEVICE, OUTPUT_DEVICE, student_flow().
"""
from __future__ import annotations

import shutil
import struct
import subprocess
import sys
import wave
from pathlib import Path

# TODO: ALSA capture device, e.g. "plughw:1,0" if mic is card 1. "" = default capture.
INPUT_DEVICE = ""

# TODO: ALSA playback device, e.g. "plughw:0,0". "" = default playback.
OUTPUT_DEVICE = ""

_LESSON_DIR = Path(__file__).resolve().parent
CAPTURE_FILE = _LESSON_DIR / "capture_lesson5.wav"

# Optional: short “reply” WAV if you do not want to replay your own recording (less feedback risk)
_REPLY_CANDIDATES = (
    _LESSON_DIR / "reply.wav",
    Path("/usr/share/sounds/alsa/Front_Center.wav"),
)


def student_flow():
    # Suggested flow (see LESSON_5_GUIDE.txt):
    #
    # require_tools()
    # record_wav(3, CAPTURE_FILE, INPUT_DEVICE)
    # level = rough_peak_level(CAPTURE_FILE)
    # print(...)  # show level 0..1
    # play_wav(CAPTURE_FILE, OUTPUT_DEVICE)   # hear what you recorded — keep volume low
    #   OR: play_wav(find_reply_wav(), OUTPUT_DEVICE)
    pass


def run_with_guard():
    try:
        student_flow()
    except ValueError as e:
        print(f"Input error: {e}")
    except RuntimeError as e:
        print(f"Setup error: {e}")
    except FileNotFoundError as e:
        print(f"Missing program or file: {e}")
    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Lesson run finished.")


def main():
    run_with_guard()


def require_tools() -> None:
    """Raise FileNotFoundError if arecord/aplay are not on PATH."""
    for name in ("arecord", "aplay"):
        if shutil.which(name) is None:
            raise FileNotFoundError(f"Missing '{name}'. Install alsa-utils (e.g. apt install alsa-utils).")


def record_wav(duration_sec: int, out_path: Path, device: str = "") -> None:
    """
    Record mono 16-bit PCM WAV from the default or given capture device.
    duration_sec: whole seconds (typical 2–5 for class).
    """
    if duration_sec < 1 or duration_sec > 30:
        raise ValueError("duration_sec: use something like 2–10 for class demos.")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "arecord",
        "-q",
        "-f",
        "S16_LE",
        "-r",
        "16000",
        "-c",
        "1",
        "-d",
        str(int(duration_sec)),
        str(out_path),
    ]
    d = (device or "").strip()
    if d:
        cmd[1:1] = ["-D", d]

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=duration_sec + 30)
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip()
        raise RuntimeError(f"arecord failed (exit {r.returncode}): {err or 'no stderr'}")


def rough_peak_level(wav_path: Path) -> float:
    """
    Very small 'level meter': peak sample magnitude as 0.0–1.0 (not dB, not calibrated).
    """
    wav_path = Path(wav_path)
    if not wav_path.is_file():
        raise ValueError(f"Not a file: {wav_path}")
    with wave.open(str(wav_path), "rb") as w:
        sw = w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if sw != 2 or len(raw) < 2:
        return 0.0
    mx = 0
    for i in range(0, len(raw) - 1, 2):
        v = struct.unpack_from("<h", raw, i)[0]
        mx = max(mx, abs(v))
    return min(1.0, mx / 32768.0)


def play_wav(path: Path | str, device: str = "") -> None:
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    cmd = ["aplay", "-q"]
    d = (device or "").strip()
    if d:
        cmd.extend(["-D", d])
    cmd.append(str(path))
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip()
        raise RuntimeError(f"aplay failed (exit {r.returncode}): {err or 'no stderr'}")


def find_reply_wav() -> Path:
    """Optional factory WAV so you can play a known clip instead of replaying the capture."""
    for p in _REPLY_CANDIDATES:
        if p.is_file():
            return p
    raise RuntimeError("No reply.wav next to challenge.py and no system Front_Center.wav fallback.")


def print_mic_speaker_checklist() -> None:
    lines = [
        "",
        "=== Mic + speaker checklist ===",
        "1) arecord -l  — note card/device for IN; aplay -l  — for OUT.",
        "2) Match INPUT_DEVICE / OUTPUT_DEVICE (e.g. plughw:1,0 and plughw:0,0) or leave \"\" to try defaults.",
        "3) Feedback: lower speaker volume in alsamixer; move mic; use short playback.",
        "4) Permissions: user may need to be in 'audio' group for some images.",
        "5) Wrong device: silence or noise — change -D strings one step at a time.",
        "",
    ]
    print("\n".join(lines), file=sys.stderr)


if __name__ == "__main__":
    main()
