"""
Lesson 10 — Voice beat sequencer (Teachable Machine, Module 10).

Phase A: speak hit names in order (classes you trained, e.g. drum, snare1).
         Say the STOP class name to finish recording the pattern.
Phase B: loop playback of that pattern on the speaker until Ctrl+C, or STOP
         heard between loops with high confidence.

Uses ../tm_audio_runtime.py (same stack as Lessons 8–9).

Edit: BEAT_LABEL_TO_WAV, STOP_CLASS_NAME, IGNORE_LABELS, MIN_SCORE, BEAT_MIN_SCORE,
      STOP_MIN_SCORE, MAX_PATTERN_LEN, BEAT_GAP_SEC, LOOP_GAP_SEC, FLASH_LED_ON_BEAT,
      LED_BEAT_PIN, ON_STATE_KEYWORD, SAMPLE_RATE, MIC_DEVICE, OUTPUT_DEVICE, student_flow().
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

_LESSON_DIR = Path(__file__).resolve().parent
_BEAT_KIT = _LESSON_DIR / "sounds" / "beat_kit"
if str(_LESSON_DIR.parent) not in sys.path:
    sys.path.insert(0, str(_LESSON_DIR.parent))

import tm_audio_runtime as tm

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None  # type: ignore

LABELS_PATH = _LESSON_DIR / "labels.txt"
SAMPLE_RATE = 16000
MIC_DEVICE: int | str | None = None
OUTPUT_DEVICE = ""

LOOP_SLEEP_SEC = 0.08
MIN_SCORE = 0.55
BEAT_MIN_SCORE = 0.62
STOP_MIN_SCORE = 0.7

MAX_PATTERN_LEN = 16
# Silence pad after each hit inside the pattern
BEAT_GAP_SEC = 0.12
# Gap after one full pass before optional STOP listen + next pass
LOOP_GAP_SEC = 0.35

IGNORE_LABELS: frozenset[str] = frozenset(
    {"Background Noise", "background", "Background", "Noise"}
)

# TODO: Teachable Machine class name that ends pattern capture and can stop the loop.
STOP_CLASS_NAME = "stop"

# TODO: Keys = TM class names for each drum voice. Values = WAV path (beat_kit/ or absolute).
# Fill after you train; placeholders point at Pi ALSA demos until you add real files.
_ALSA = Path("/usr/share/sounds/alsa")
BEAT_LABEL_TO_WAV: dict[str, Path | str] = {
    "drum": _BEAT_KIT / "drum.wav",
    "snare1": _BEAT_KIT / "snare1.wav",
    "snare2": _ALSA / "Front_Center.wav",
    "bass": _ALSA / "Front_Left.wav",
    "hi-hat": _ALSA / "Front_Right.wav",
}

REMOVE_DC_OFFSET = True
AMBIENT_CALIB_SEC = 0.8
AMBIENT_GATE_MULT = 2.0
AMBIENT_DYNAMIC_MIN_SCORE = False
AMBIENT_DYN_MAX_ADD = 0.12

# Optional: flash kit LED on each hit (BCM pin; VoiceKit red LED often 26).
FLASH_LED_ON_BEAT = True
LED_BEAT_PIN = 26
ON_STATE_KEYWORD = "HIGH"
LED_FLASH_SEC = 0.04

# Ignore same label twice in a row within this many seconds (debounce).
DEBOUNCE_SEC = 0.35


def student_flow() -> None:
    run_beat_sequencer()


def run_with_guard() -> None:
    try:
        student_flow()
    except ValueError as e:
        print(f"Input error: {e}")
    except RuntimeError as e:
        print(f"Setup error: {e}")
    except FileNotFoundError as e:
        print(f"Missing: {e}")
    except KeyboardInterrupt:
        print("Stopped.")
    except Exception as e:
        print(f"Unexpected: {e}")
    finally:
        gpio_cleanup_safe()
        print("Lesson finished.")


def main() -> None:
    run_with_guard()


_ON_STATE: int | None = None
_LED_GPIO_READY = False


def run_beat_sequencer() -> None:
    if not BEAT_LABEL_TO_WAV:
        raise ValueError("Fill BEAT_LABEL_TO_WAV with your TM class names and WAV paths.")
    tm.ensure_audio_deps()
    model = tm.resolve_model_path(_LESSON_DIR)
    if not LABELS_PATH.is_file():
        raise FileNotFoundError(f"Missing {LABELS_PATH.name}")
    labels = tm.load_labels(LABELS_PATH)
    bundle = tm.load_tflite_bundle(model, labels)
    ignore_low = tm.ignore_labels_normalized(IGNORE_LABELS)
    gpio_ok = setup_gpio_beat_led()

    print(f"Model: {model.name} | TM labels: {labels}")
    print("Phase A — speak your pattern using:", ", ".join(sorted(BEAT_LABEL_TO_WAV.keys())))
    print(f"Say {STOP_CLASS_NAME!r} when finished (or hit max {MAX_PATTERN_LEN} hits).\n")

    ambient = 0.0
    if AMBIENT_CALIB_SEC > 0:
        print(f"Quiet… calibrating ~{AMBIENT_CALIB_SEC:.1f}s")
        ambient = tm.calibrate_ambient_floor_rms(
            AMBIENT_CALIB_SEC, SAMPLE_RATE, MIC_DEVICE, REMOVE_DC_OFFSET
        )
        print(f"Ambient RMS ≈ {ambient:.5f}\n")

    pattern: list[str] = []
    last_label_time: dict[str, float] = {}

    while len(pattern) < MAX_PATTERN_LEN:
        raw = tm.record_mono_float32(bundle.num_samples, SAMPLE_RATE, MIC_DEVICE)
        audio = tm.preprocess_inmp441(raw, REMOVE_DC_OFFSET)
        wrms = tm.window_rms(audio)
        if ambient > 0 and AMBIENT_GATE_MULT > 0 and wrms < ambient * AMBIENT_GATE_MULT:
            time.sleep(LOOP_SLEEP_SEC)
            continue
        label, score, _ = tm.predict(bundle, audio)
        if label is None:
            time.sleep(LOOP_SLEEP_SEC)
            continue
        min_use = tm.effective_min_score(
            MIN_SCORE, wrms, ambient,
            dyn_enabled=AMBIENT_DYNAMIC_MIN_SCORE,
            dyn_max_add=AMBIENT_DYN_MAX_ADD,
        )
        if score < min_use:
            time.sleep(LOOP_SLEEP_SEC)
            continue
        low = label.strip().lower()
        if low in ignore_low:
            time.sleep(LOOP_SLEEP_SEC)
            continue

        if label.strip().casefold() == STOP_CLASS_NAME.strip().casefold() and score >= STOP_MIN_SCORE:
            print(f"Stop token heard ({score:.2f}). Pattern recorded: {pattern}")
            break

        if label in BEAT_LABEL_TO_WAV and score >= BEAT_MIN_SCORE:
            now = time.monotonic()
            if (
                pattern
                and pattern[-1] == label
                and now - last_label_time.get(label, 0) < DEBOUNCE_SEC
            ):
                time.sleep(LOOP_SLEEP_SEC)
                continue
            pattern.append(label)
            last_label_time[label] = now
            print(f"  + {label!r} (score {score:.2f}) → pattern len {len(pattern)}")

        time.sleep(LOOP_SLEEP_SEC)
    else:
        print(f"Max pattern length ({MAX_PATTERN_LEN}) reached: {pattern}")

    if not pattern:
        raise RuntimeError("Empty pattern — say at least one drum class before stop.")

    print("\nPhase B — looping pattern. Ctrl+C to quit.")
    print(f"Between full loops, say {STOP_CLASS_NAME!r} to exit cleanly.\n")

    while True:
        for hit in pattern:
            path = resolve_beat_wav(hit)
            if gpio_ok:
                led_beat_flash()
            try:
                tm.play_wav(path, OUTPUT_DEVICE)
            except Exception as e:
                print(f"play {hit}: {e}")
            time.sleep(BEAT_GAP_SEC)

        time.sleep(LOOP_GAP_SEC)
        # One-window listen for STOP between loop iterations
        raw = tm.record_mono_float32(bundle.num_samples, SAMPLE_RATE, MIC_DEVICE)
        audio = tm.preprocess_inmp441(raw, REMOVE_DC_OFFSET)
        wrms = tm.window_rms(audio)
        if ambient > 0 and AMBIENT_GATE_MULT > 0 and wrms < ambient * AMBIENT_GATE_MULT:
            continue
        label, score, _ = tm.predict(bundle, audio)
        if (
            label
            and label.strip().casefold() == STOP_CLASS_NAME.strip().casefold()
            and score >= STOP_MIN_SCORE
        ):
            print(f"Heard {STOP_CLASS_NAME!r} ({score:.2f}) — exiting loop.")
            break


def resolve_beat_wav(hit: str) -> Path:
    raw = BEAT_LABEL_TO_WAV.get(hit)
    if raw is None:
        raise KeyError(f"No WAV mapped for hit {hit!r}. Add it to BEAT_LABEL_TO_WAV.")
    p = tm.resolve_sound_path(_LESSON_DIR, raw)
    if p.is_file():
        return p
    for fb in (
        Path("/usr/share/sounds/alsa/Front_Center.wav"),
        Path("/usr/share/sounds/alsa/Front_Left.wav"),
    ):
        if fb.is_file():
            return fb
    raise FileNotFoundError(f"No WAV for {hit} and no system fallback.")


def setup_gpio_beat_led() -> bool:
    global _ON_STATE, _LED_GPIO_READY
    if not FLASH_LED_ON_BEAT or GPIO is None:
        if GPIO is None and FLASH_LED_ON_BEAT:
            print("(GPIO unavailable — LED flash disabled.)")
        return False
    k = ON_STATE_KEYWORD.strip().upper()
    if k == "HIGH":
        _ON_STATE = GPIO.HIGH
    elif k == "LOW":
        _ON_STATE = GPIO.LOW
    else:
        raise ValueError('ON_STATE_KEYWORD must be "HIGH" or "LOW".')
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_BEAT_PIN, GPIO.OUT)
    GPIO.output(LED_BEAT_PIN, GPIO.LOW if _ON_STATE == GPIO.HIGH else GPIO.HIGH)
    _LED_GPIO_READY = True
    return True


def led_beat_flash() -> None:
    if GPIO is None or _ON_STATE is None:
        return
    GPIO.output(LED_BEAT_PIN, _ON_STATE)
    time.sleep(LED_FLASH_SEC)
    GPIO.output(LED_BEAT_PIN, GPIO.LOW if _ON_STATE == GPIO.HIGH else GPIO.HIGH)


def gpio_cleanup_safe() -> None:
    global _LED_GPIO_READY
    if GPIO is None or not _LED_GPIO_READY:
        return
    try:
        GPIO.output(LED_BEAT_PIN, GPIO.LOW)
        GPIO.cleanup()
    except Exception:
        pass
    _LED_GPIO_READY = False


if __name__ == "__main__":
    main()
