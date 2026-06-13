"""
Lesson 8 challenge — Barnyard soundboard with Teachable Machine (Module 8).

Uses a small stack: TensorFlow Lite (tflite_runtime) + sounddevice + labels.txt.
Export your TM audio model as TensorFlow Lite, add labels.txt from the zip, map
class names to WAV files.

Edit: LABEL_TO_SOUND, IGNORE_LABELS, MIN_SCORE, COOLDOWN_SEC, OUTPUT_DEVICE,
      SAMPLE_RATE, MIC_DEVICE, INMP441 / ambient knobs (below), student_flow().
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    try:
        from tensorflow.lite import Interpreter  # type: ignore
    except ImportError:
        Interpreter = None  # type: ignore

try:
    import sounddevice as sd
except ImportError:
    sd = None  # type: ignore

_LESSON_DIR = Path(__file__).resolve().parent

# First existing file wins (rename your export to match, or add a symlink).
_MODEL_CANDIDATES = (
    _LESSON_DIR / "model.tflite",
    _LESSON_DIR / "soundclassifier_with_metadata.tflite",
)

LABELS_PATH = _LESSON_DIR / "labels.txt"

# TODO: Must match your model / training (common TM waveform exports: 16000).
SAMPLE_RATE = 16000

# TODO: sounddevice input device: None = default, or an int index, or a host API string — see sd.query_devices()
MIC_DEVICE: int | str | None = None

# TODO: ALSA playback device for aplay (Lesson 4). "" = default.
OUTPUT_DEVICE = ""

# Pause between inference windows (seconds); lower = snappier, more CPU.
LOOP_SLEEP_SEC = 0.1

# TODO: Ignore weak guesses so room noise does not trigger the zoo.
MIN_SCORE = 0.65

# TODO: Seconds after a sound before another can play (reduces double-fires).
COOLDOWN_SEC = 0.8

# --- INMP441 (I2S mic) — ambient / DC helpers (see preprocess_inmp441, calibrate_ambient_floor_rms) ---
# Remove DC offset per window (reduces slow drift some I2S front-ends show on a quiet line).
REMOVE_DC_OFFSET = True

# Seconds of “room only” capture to estimate ambient RMS. Set 0 to skip calibration.
AMBIENT_CALIB_SEC = 1.5

# If > 0 and calibration ran: skip the neural net when the window is quieter than
#   ambient_floor_rms * AMBIENT_GATE_MULT
# (saves CPU and cuts spurious triggers on near-silence / fan-only noise). Raise if real speech gets skipped.
AMBIENT_GATE_MULT = 2.5

# When True, slightly raise MIN_SCORE in louder moments vs calibrated floor (classroom HVAC).
AMBIENT_DYNAMIC_MIN_SCORE = False
AMBIENT_DYN_MAX_ADD = 0.12  # cap on extra threshold added to MIN_SCORE

# TODO: Keys must match labels in labels.txt (same spelling as Teachable Machine). Values = Path or str.
LABEL_TO_SOUND: dict[str, Path | str] = {}

# Class names that should never trigger a sound (e.g. background / noise bucket).
IGNORE_LABELS: frozenset[str] = frozenset(
    {
        "Background Noise",
        "background",
        "Background",
    }
)


def student_flow() -> None:
    run_barnyard_soundboard()


def run_with_guard() -> None:
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


def main() -> None:
    run_with_guard()


def resolve_model_path() -> Path:
    for p in _MODEL_CANDIDATES:
        if p.is_file():
            return p
    raise FileNotFoundError(
        "No TFLite model found. Copy one of these into the lesson folder:\n"
        f"  {', '.join(str(p.name) for p in _MODEL_CANDIDATES)}\n"
        "(Teachable Machine: Export model → TensorFlow Lite → unzip.)"
    )


def resolve_sound_path(raw: Path | str) -> Path:
    """Turn LABEL_TO_SOUND values into Path; relative paths resolve against this lesson folder."""
    p = Path(raw)
    if p.is_file():
        return p
    alt = _LESSON_DIR / p
    if alt.is_file():
        return alt
    return p


def window_rms(x: np.ndarray) -> float:
    xf = np.asarray(x, dtype=np.float32)
    return float(np.sqrt(np.mean(xf * xf, dtype=np.float64) + 1e-20))


def preprocess_inmp441(samples: np.ndarray, remove_dc: bool) -> np.ndarray:
    """Light conditioning for INMP441-style I2S mics before the TM waveform model."""
    x = np.asarray(samples, dtype=np.float32).copy()
    if remove_dc:
        x -= np.float32(np.mean(x))
    return x


def calibrate_ambient_floor_rms(
    duration_sec: float,
    sample_rate: int,
    device: int | str | None,
    remove_dc: bool,
) -> float:
    """
    Estimate “room noise” RMS while it is quiet: stay silent during calibration.
    Uses the median of short-window RMS values (robust to a cough or chair tap).
    """
    n = max(int(duration_sec * sample_rate), sample_rate // 4)
    raw = record_mono_float32(n, sample_rate, device)
    x = preprocess_inmp441(raw, remove_dc)
    hop = max(sample_rate // 10, 400)
    step = max(hop // 2, 1)
    rmss: list[float] = []
    for i in range(0, len(x) - hop + 1, step):
        rmss.append(window_rms(x[i : i + hop]))
    if not rmss:
        return window_rms(x)
    return float(np.median(np.asarray(rmss, dtype=np.float64)))


def effective_min_score(base_min: float, window_rms: float, ambient_floor: float) -> float:
    """Optionally tighten MIN_SCORE when the current window is much louder than the quiet floor."""
    if not AMBIENT_DYNAMIC_MIN_SCORE or ambient_floor <= 0:
        return base_min
    ratio = window_rms / (ambient_floor + 1e-9)
    bump = min(AMBIENT_DYN_MAX_ADD, max(0.0, (ratio - 2.0) * 0.04))
    return float(min(0.95, base_min + bump))


def run_barnyard_soundboard() -> None:
    ensure_model_and_deps()
    if not LABEL_TO_SOUND:
        raise ValueError(
            "LABEL_TO_SOUND is empty. Add entries whose keys match labels.txt "
            "exactly (same names as in Teachable Machine)."
        )
    model_path = resolve_model_path()
    labels = load_labels(LABELS_PATH)
    bundle = load_tflite_bundle(model_path, labels)

    print(f"Model: {model_path.name}")
    print(f"Labels: {len(labels)} classes → {LABELS_PATH.name}")
    print(f"Input shape: {bundle.input_tensor_shape}, dtype: {bundle.input_dtype}")
    print(f"Sample rate: {SAMPLE_RATE} Hz (set SAMPLE_RATE to match your export if wrong)")

    ambient_floor = 0.0
    if AMBIENT_CALIB_SEC and AMBIENT_CALIB_SEC > 0:
        print(
            f"Calibrating ambient noise (~{AMBIENT_CALIB_SEC:.1f}s) — stay quiet… "
            "(INMP441 / room tone only)"
        )
        ambient_floor = calibrate_ambient_floor_rms(
            AMBIENT_CALIB_SEC, SAMPLE_RATE, MIC_DEVICE, REMOVE_DC_OFFSET
        )
        print(
            f"Ambient floor RMS ≈ {ambient_floor:.5f} "
            f"(gate: x{AMBIENT_GATE_MULT} → skip infer below {ambient_floor * AMBIENT_GATE_MULT:.5f})"
        )
    print(f"Listening… min_score={MIN_SCORE}, Ctrl+C to stop\n")

    ignore_low = ignore_labels_normalized(IGNORE_LABELS)
    last_fire = 0.0
    while True:
        audio = record_mono_float32(bundle.num_samples, SAMPLE_RATE, MIC_DEVICE)
        audio = preprocess_inmp441(audio, REMOVE_DC_OFFSET)
        wrms = window_rms(audio)

        if ambient_floor > 0 and AMBIENT_GATE_MULT > 0 and wrms < ambient_floor * AMBIENT_GATE_MULT:
            time.sleep(LOOP_SLEEP_SEC)
            continue

        label, score = predict(bundle, audio)

        if label is None:
            time.sleep(LOOP_SLEEP_SEC)
            continue

        now = time.monotonic()
        min_use = effective_min_score(MIN_SCORE, wrms, ambient_floor)
        if score < min_use:
            time.sleep(LOOP_SLEEP_SEC)
            continue
        if label.strip().lower() in ignore_low:
            time.sleep(LOOP_SLEEP_SEC)
            continue
        if now - last_fire < COOLDOWN_SEC:
            time.sleep(LOOP_SLEEP_SEC)
            continue

        raw = LABEL_TO_SOUND.get(label)
        if raw is None:
            print(f"[{label}] score={score:.2f} (no WAV in LABEL_TO_SOUND)")
            time.sleep(LOOP_SLEEP_SEC)
            continue
        path = resolve_sound_path(raw)
        if not path.is_file():
            print(f"[{label}] score={score:.2f} missing file: {path}")
            time.sleep(LOOP_SLEEP_SEC)
            continue

        print(f"→ {label} ({score:.2f}) play {path.name}")
        try:
            play_wav(path, OUTPUT_DEVICE)
        except Exception as e:
            print(f"Playback error: {e}")
        last_fire = now
        time.sleep(LOOP_SLEEP_SEC)


def ignore_labels_normalized(ignore: frozenset[str]) -> frozenset[str]:
    return frozenset(s.strip().lower() for s in ignore)


def ensure_model_and_deps() -> None:
    if Interpreter is None:
        raise RuntimeError(
            "No TFLite interpreter. Install:\n"
            "  python3 -m pip install tflite-runtime\n"
            "or (larger): pip install tensorflow"
        )
    if sd is None:
        raise RuntimeError(
            "sounddevice is not installed.\n"
            "  python3 -m pip install sounddevice\n"
            "On Raspberry Pi OS you may need: sudo apt install portaudio19-dev"
        )
    resolve_model_path()
    if not LABELS_PATH.is_file():
        raise FileNotFoundError(
            f"Missing {LABELS_PATH.name} next to challenge.py. "
            "It is usually inside the Teachable Machine TensorFlow Lite export zip."
        )


def load_labels(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
    labels: list[str] = []
    for line in raw:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # "0 Background Noise" or "0 Background Noise" from TM
        m = re.match(r"^\d+\s+(.+)$", line)
        if m:
            labels.append(m.group(1).strip())
        else:
            labels.append(line)
    if not labels:
        raise ValueError(f"No labels parsed from {path}")
    return labels


def load_tflite_bundle(model_path: Path, labels: list[str]) -> "TfliteBundle":
    interpreter = Interpreter(model_path=str(model_path))
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]

    ishape = tuple(int(s) for s in input_details["shape"])
    if len(ishape) == 4:
        raise RuntimeError(
            "Model input is 4D (likely a spectrogram). This lesson expects a "
            "waveform model (float32 audio window, e.g. shape [1, N]). "
            "Re-export from Teachable Machine or use a model that takes raw samples."
        )

    if len(ishape) == 2 and ishape[0] == 1:
        num_samples = ishape[1]
    elif len(ishape) == 1:
        num_samples = ishape[0]
    else:
        num_samples = int(np.prod(ishape))

    dtype = input_details.get("dtype") or np.float32

    if np.issubdtype(dtype, np.floating):
        z = np.zeros(ishape, dtype=np.float32)
        interpreter.set_tensor(input_details["index"], z)
        interpreter.invoke()
        out = np.asarray(interpreter.get_tensor(output_details["index"])).reshape(-1)
        if len(labels) != out.size:
            print(
                f"Warning: labels.txt has {len(labels)} entries but model output size is {out.size}. "
                "Indices may not match class names."
            )

    return TfliteBundle(
        interpreter=interpreter,
        input_index=input_details["index"],
        output_index=output_details["index"],
        num_samples=num_samples,
        input_dtype=dtype,
        input_tensor_shape=ishape,
        labels=labels,
    )


class TfliteBundle:
    __slots__ = (
        "interpreter",
        "input_index",
        "output_index",
        "num_samples",
        "input_dtype",
        "input_tensor_shape",
        "labels",
    )

    def __init__(
        self,
        interpreter: object,
        input_index: int,
        output_index: int,
        num_samples: int,
        input_dtype: object,
        input_tensor_shape: tuple[int, ...],
        labels: list[str],
    ) -> None:
        self.interpreter = interpreter
        self.input_index = input_index
        self.output_index = output_index
        self.num_samples = num_samples
        self.input_dtype = input_dtype
        self.input_tensor_shape = input_tensor_shape
        self.labels = labels


def record_mono_float32(num_samples: int, sample_rate: int, device: int | str | None) -> np.ndarray:
    """Block until one window of mono audio is captured."""
    audio = sd.rec(
        num_samples,
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
        device=device,
    )
    sd.wait()
    return np.asarray(audio, dtype=np.float32).flatten()


def predict(bundle: TfliteBundle, audio_flat: np.ndarray) -> tuple[str | None, float]:
    """Run TFLite once; return (label, score) for argmax class."""
    if audio_flat.shape[0] != bundle.num_samples:
        raise ValueError(
            f"Expected {bundle.num_samples} samples, got {audio_flat.shape[0]}. "
            "Check SAMPLE_RATE and model export."
        )

    x = audio_flat.astype(np.float32)
    if not np.issubdtype(bundle.input_dtype, np.floating):
        raise RuntimeError(
            f"Model input dtype is {bundle.input_dtype}; this lesson expects float32 "
            "waveform input (typical Teachable Machine export). Re-export or use a float model."
        )

    inp = x.reshape(bundle.input_tensor_shape)

    bundle.interpreter.set_tensor(bundle.input_index, inp)
    bundle.interpreter.invoke()
    out = bundle.interpreter.get_tensor(bundle.output_index)
    out = np.asarray(out, dtype=np.float32).reshape(-1)

    if out.size == 0:
        return None, 0.0

    # Softmax if logits (not already probabilities)
    sm = _maybe_softmax(out)
    idx = int(np.argmax(sm))
    score = float(sm[idx])
    if idx >= len(bundle.labels):
        return None, score
    return bundle.labels[idx].strip(), score


def _maybe_softmax(logits: np.ndarray) -> np.ndarray:
    logits = logits.astype(np.float64)
    if np.all(logits >= 0.0) and np.all(logits <= 1.01) and 0.99 <= np.sum(logits) <= 1.01:
        return logits.astype(np.float32)
    z = logits - np.max(logits)
    e = np.exp(z)
    s = e / np.sum(e)
    return s.astype(np.float32)


def play_wav(path: Path | str, device: str = "") -> None:
    """Play a WAV through the speaker path (aplay)."""
    if shutil.which("aplay") is None:
        raise FileNotFoundError("aplay not found. Install alsa-utils (e.g. apt install alsa-utils).")
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


def print_audio_hint() -> None:
    lines = [
        "",
        "=== Audio quick hints (Lesson 8) ===",
        "1) model.tflite (or soundclassifier_with_metadata.tflite) + labels.txt in this folder.",
        "2) LABEL_TO_SOUND keys must match labels.txt lines (same as TM class names).",
        "3) SAMPLE_RATE must match your model (often 16000).",
        "4) Speaker: aplay -l  then set OUTPUT_DEVICE",
        "5) pip: python3 -m pip install -r requirements.txt",
        "",
    ]
    print("\n".join(lines), file=sys.stderr)


if __name__ == "__main__":
    main()
