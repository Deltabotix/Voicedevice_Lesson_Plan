"""
Lesson 9 — Secret clubhouse knock (Teachable Machine, Module 9).

Train password sound(s) + background in TM, export TFLite + labels.txt.
If the model hears an UNLOCK label with high confidence → success LED + WAV.
If it hears a confident non-password, non-background label → “no” LED + WAV.
Uses shared tm_audio_runtime (parent lessons/ folder).

Edit: UNLOCK_LABELS, IGNORE_LABELS, MIN_SCORE, UNLOCK_MIN_SCORE, INTRUDER_MIN_SCORE,
      COOLDOWN_SEC, SUCCESS_WAV, DENY_WAV, LED_OK_PIN, LED_NO_PIN, ON_STATE_KEYWORD,
      SAMPLE_RATE, MIC_DEVICE, OUTPUT_DEVICE, student_flow().
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

_LESSON_DIR = Path(__file__).resolve().parent
if str(_LESSON_DIR.parent) not in sys.path:
    sys.path.insert(0, str(_LESSON_DIR.parent))

import tm_audio_runtime as tm

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None  # type: ignore

# --- Model / audio (same pattern as Lesson 8) ---
LABELS_PATH = _LESSON_DIR / "labels.txt"
SAMPLE_RATE = 16000
MIC_DEVICE: int | str | None = None
OUTPUT_DEVICE = ""

LOOP_SLEEP_SEC = 0.1
MIN_SCORE = 0.55  # minimum confidence to react at all
# Stricter threshold for opening the “clubhouse” (raise if false accepts).
UNLOCK_MIN_SCORE = 0.72
# Minimum confidence to treat a wrong class as an “intruder” (not background fluff).
INTRUDER_MIN_SCORE = 0.65
COOLDOWN_SEC = 1.0

REMOVE_DC_OFFSET = True
AMBIENT_CALIB_SEC = 1.2
AMBIENT_GATE_MULT = 2.5
AMBIENT_DYNAMIC_MIN_SCORE = False
AMBIENT_DYN_MAX_ADD = 0.12

# TODO: Exact TM class name(s) that unlock (can be more than one knock / word).
UNLOCK_LABELS: frozenset[str] = frozenset()

# Background / noise — no LED change, no deny sound.
IGNORE_LABELS: frozenset[str] = frozenset(
    {"Background Noise", "background", "Background", "Noise"}
)

# TODO: WAV files for feedback (system demos OK for class test).
SUCCESS_WAV: Path | str = Path("/usr/share/sounds/alsa/Front_Center.wav")
DENY_WAV: Path | str = Path("/usr/share/sounds/alsa/Front_Left.wav")

# Kit-ish defaults: “OK” = blue L1 (16), “NO” = red L2 (26). Change if your image differs.
LED_OK_PIN = 16
LED_NO_PIN = 26
ON_STATE_KEYWORD = "HIGH"


def student_flow() -> None:
    run_clubhouse()


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
        print("Interrupted.")
    except Exception as e:
        print(f"Unexpected: {e}")
    finally:
        gpio_cleanup_safe()
        print("Lesson finished.")


def main() -> None:
    run_with_guard()


def run_clubhouse() -> None:
    if not UNLOCK_LABELS:
        raise ValueError("Set UNLOCK_LABELS to your Teachable Machine password class name(s).")
    tm.ensure_audio_deps()
    model = tm.resolve_model_path(_LESSON_DIR)
    if not LABELS_PATH.is_file():
        raise FileNotFoundError(f"Missing {LABELS_PATH.name} (from TM export zip).")
    labels = tm.load_labels(LABELS_PATH)
    bundle = tm.load_tflite_bundle(model, labels)
    ignore_low = tm.ignore_labels_normalized(IGNORE_LABELS)

    on = setup_gpio_leds()
    print(f"Model: {model.name} | labels: {labels}")
    print(f"Unlock if label in {sorted(UNLOCK_LABELS)} with score ≥ {UNLOCK_MIN_SCORE}")
    print("Ctrl+C to exit.\n")

    ambient = 0.0
    if AMBIENT_CALIB_SEC > 0:
        print(f"Quiet please — calibrating ~{AMBIENT_CALIB_SEC:.1f}s…")
        ambient = tm.calibrate_ambient_floor_rms(
            AMBIENT_CALIB_SEC, SAMPLE_RATE, MIC_DEVICE, REMOVE_DC_OFFSET
        )
        print(f"Ambient RMS ≈ {ambient:.5f}\n")

    last_fire = 0.0
    while True:
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

        now = time.monotonic()
        if now - last_fire < COOLDOWN_SEC:
            time.sleep(LOOP_SLEEP_SEC)
            continue

        if label in UNLOCK_LABELS and score >= UNLOCK_MIN_SCORE:
            print(f"UNLOCK {label!r} ({score:.2f})")
            if on:
                led_set(LED_NO_PIN, False)
                led_set(LED_OK_PIN, True)
            try:
                tm.play_wav(tm.resolve_sound_path(_LESSON_DIR, SUCCESS_WAV), OUTPUT_DEVICE)
            except Exception as e:
                print(f"Success WAV: {e}")
            time.sleep(0.35)
            if on:
                led_set(LED_OK_PIN, False)
            last_fire = now
        elif score >= INTRUDER_MIN_SCORE and label not in UNLOCK_LABELS:
            print(f"DENY {label!r} ({score:.2f})")
            if on:
                led_set(LED_OK_PIN, False)
                led_set(LED_NO_PIN, True)
            try:
                tm.play_wav(tm.resolve_sound_path(_LESSON_DIR, DENY_WAV), OUTPUT_DEVICE)
            except Exception as e:
                print(f"Deny WAV: {e}")
            time.sleep(0.35)
            if on:
                led_set(LED_NO_PIN, False)
            last_fire = now

        time.sleep(LOOP_SLEEP_SEC)


_ON_STATE: int | None = None


def setup_gpio_leds() -> bool:
    """Return False if not on a Pi / no GPIO."""
    global _ON_STATE
    if GPIO is None:
        print("(GPIO not available — LED feedback skipped.)")
        return False
    k = ON_STATE_KEYWORD.strip().upper()
    if k == "HIGH":
        _ON_STATE = GPIO.HIGH
    elif k == "LOW":
        _ON_STATE = GPIO.LOW
    else:
        raise ValueError('ON_STATE_KEYWORD must be "HIGH" or "LOW".')
    GPIO.setmode(GPIO.BCM)
    for pin in (LED_OK_PIN, LED_NO_PIN):
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW if _ON_STATE == GPIO.HIGH else GPIO.HIGH)
    return True


def led_set(pin: int, on: bool) -> None:
    if GPIO is None or _ON_STATE is None:
        return
    if on:
        GPIO.output(pin, _ON_STATE)
    else:
        GPIO.output(pin, GPIO.LOW if _ON_STATE == GPIO.HIGH else GPIO.HIGH)


def gpio_cleanup_safe() -> None:
    if GPIO is None:
        return
    try:
        for pin in (LED_OK_PIN, LED_NO_PIN):
            try:
                GPIO.output(pin, GPIO.LOW)
            except Exception:
                pass
        GPIO.cleanup()
    except Exception:
        pass


if __name__ == "__main__":
    main()
