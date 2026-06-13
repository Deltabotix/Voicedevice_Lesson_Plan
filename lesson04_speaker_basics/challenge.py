"""
Lesson 4 challenge — Speaker: play a test sound and learn the audio chain (Module 4).
Uses aplay(1). Edit: AUDIO_DEVICE, student_flow().
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# TODO: ALSA device string. Examples: "plughw:0,0" , "hw:0,0" , "default"
# Leave "" to let aplay use the default device (often fine on a classroom Pi).
AUDIO_DEVICE = ""

# Paths tried in order: lesson folder first, then common Raspberry Pi OS / ALSA demos
_TEST_CANDIDATES = (
    Path(__file__).resolve().parent / "test.wav",
    Path("/usr/share/sounds/alsa/Front_Left.wav"),
    Path("/usr/share/sounds/alsa/Front_Center.wav"),
    Path("/usr/share/sounds/alsa/Rear_Left.wav"),
)


def student_flow():
    # Suggested flow (see LESSON_4_GUIDE.txt):
    #
    # path = find_test_audio()
    # play_wav(path, AUDIO_DEVICE)
    #
    # If you add experiments: try_play_wav(...) and on failure call print_audio_checklist()
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


def find_test_audio() -> Path:
    """Return the first existing WAV path from the lesson list."""
    for p in _TEST_CANDIDATES:
        if p.is_file():
            return p
    raise RuntimeError(
        "No test WAV found. Add a file named test.wav next to challenge.py, "
        "or install alsa-utils / use an image that ships /usr/share/sounds/alsa/*.wav"
    )


def play_wav(path: Path | str, device: str = "") -> None:
    """
    Play a WAV file through the speaker path (aplay).
    device: non-empty string passed to aplay -D (ALSA device name).
    """
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


def try_play_wav(path: Path | str, device: str = "") -> bool:
    """Same as play_wav but returns False instead of raising on failure."""
    try:
        play_wav(path, device)
        return True
    except Exception:
        return False


def print_audio_checklist() -> None:
    """Short on-screen checklist when you hear nothing or errors."""
    lines = [
        "",
        "=== Speaker / audio quick checklist ===",
        "1) Headphones unplugged? Speaker wired to amp (MAX98357A) and power?",
        "2) Volume: alsamixer (not muted). Or: amixer scontrols",
        "3) Right sound card index? Try: aplay -l   and match plughw:CARD,DEVICE",
        "4) This lesson uses: aplay. Is it installed? which aplay",
        "5) File format: this step expects WAV (PCM). MP3 needs mpg123 instead.",
        "6) Put test.wav in this lesson folder if system demos are missing.",
        "",
    ]
    print("\n".join(lines), file=sys.stderr)


if __name__ == "__main__":
    main()
