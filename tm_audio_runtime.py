"""
Shared helpers for Teachable Machine waveform TFLite + sounddevice (Lessons 8–10).

Import from a lesson folder:
    import sys
    from pathlib import Path
    _L = Path(__file__).resolve().parent
    sys.path.insert(0, str(_L.parent))
    import tm_audio_runtime as tm
"""
from __future__ import annotations

import re
import shutil
import subprocess
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


def ensure_audio_deps() -> None:
    if Interpreter is None:
        raise RuntimeError(
            "No TFLite interpreter. Install: python3 -m pip install tflite-runtime"
        )
    if sd is None:
        raise RuntimeError(
            "sounddevice missing. pip install sounddevice; "
            "on Pi: sudo apt install portaudio19-dev"
        )


def default_model_candidates(lesson_dir: Path) -> tuple[Path, ...]:
    return (
        lesson_dir / "model.tflite",
        lesson_dir / "soundclassifier_with_metadata.tflite",
    )


def resolve_model_path(lesson_dir: Path, candidates: tuple[Path, ...] | None = None) -> Path:
    cands = candidates or default_model_candidates(lesson_dir)
    for p in cands:
        if p.is_file():
            return p
    raise FileNotFoundError(
        "No TFLite model in lesson folder. Expected one of: "
        + ", ".join(p.name for p in cands)
    )


def resolve_sound_path(lesson_dir: Path, raw: Path | str) -> Path:
    p = Path(raw)
    if p.is_file():
        return p
    alt = lesson_dir / p
    if alt.is_file():
        return alt
    return p


def load_labels(path: Path) -> list[str]:
    """
    Parse labels.txt. Lines like ``0 Name`` are sorted by leading index when all lines
    use that format (fixes wrong file order vs model output indices).
    """
    raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
    indexed: list[tuple[int, str]] = []
    plain: list[str] = []
    for line in raw:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^(\d+)\s+(.+)$", line)
        if m:
            indexed.append((int(m.group(1)), m.group(2).strip()))
        else:
            plain.append(line)

    if indexed and not plain:
        indexed.sort(key=lambda t: t[0])
        idxs = [i for i, _ in indexed]
        if len(set(idxs)) != len(idxs):
            raise ValueError(f"Duplicate label indices in {path}: {idxs}")
        exp = list(range(len(indexed)))
        if idxs != exp:
            print(
                f"Warning: {path.name} indices not 0..n-1 contiguous: {idxs}. "
                "Prefer labels.txt from the Teachable Machine export zip."
            )
        return [n for _, n in indexed]

    if indexed and plain:
        raise ValueError(f"{path}: cannot mix indexed and plain label lines.")
    if not indexed and not plain:
        raise ValueError(f"No labels in {path}")
    return plain


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


def load_tflite_bundle(model_path: Path, labels: list[str]) -> TfliteBundle:
    ensure_audio_deps()
    interpreter = Interpreter(model_path=str(model_path))
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()[0]
    outs = interpreter.get_output_details()
    if len(outs) > 1:
        print(
            f"Warning: {len(outs)} output tensors; using first. Names: "
            + str([o.get("name") for o in outs])
        )
    output_details = outs[0]

    ishape = tuple(int(s) for s in input_details["shape"])
    if len(ishape) == 4:
        raise RuntimeError(
            "Model input is 4D (spectrogram). These lessons expect float waveform [1, N]."
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
                f"Warning: {len(labels)} labels vs model output size {out.size}."
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


def record_mono_float32(num_samples: int, sample_rate: int, device: int | str | None) -> np.ndarray:
    ensure_audio_deps()
    audio = sd.rec(
        num_samples,
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
        device=device,
    )
    sd.wait()
    return np.asarray(audio, dtype=np.float32).flatten()


def preprocess_inmp441(samples: np.ndarray, remove_dc: bool) -> np.ndarray:
    x = np.asarray(samples, dtype=np.float32).copy()
    if remove_dc:
        x -= np.float32(np.mean(x))
    return x


def window_rms(x: np.ndarray) -> float:
    xf = np.asarray(x, dtype=np.float32)
    return float(np.sqrt(np.mean(xf * xf, dtype=np.float64) + 1e-20))


def calibrate_ambient_floor_rms(
    duration_sec: float,
    sample_rate: int,
    device: int | str | None,
    remove_dc: bool,
) -> float:
    n = max(int(duration_sec * sample_rate), sample_rate // 4)
    raw = record_mono_float32(n, sample_rate, device)
    x = preprocess_inmp441(raw, remove_dc)
    hop = max(sample_rate // 10, 400)
    step = max(hop // 2, 1)
    rmss = [window_rms(x[i : i + hop]) for i in range(0, len(x) - hop + 1, step)]
    return float(np.median(np.asarray(rmss, dtype=np.float64))) if rmss else window_rms(x)


def effective_min_score(
    base_min: float,
    window_rms: float,
    ambient_floor: float,
    *,
    dyn_enabled: bool,
    dyn_max_add: float,
) -> float:
    if not dyn_enabled or ambient_floor <= 0:
        return base_min
    ratio = window_rms / (ambient_floor + 1e-9)
    bump = min(dyn_max_add, max(0.0, (ratio - 2.0) * 0.04))
    return float(min(0.95, base_min + bump))


def predict(
    bundle: TfliteBundle,
    audio_flat: np.ndarray,
    *,
    return_probs: bool = False,
) -> tuple[str | None, float, np.ndarray | None]:
    if audio_flat.shape[0] != bundle.num_samples:
        raise ValueError(
            f"Expected {bundle.num_samples} samples, got {audio_flat.shape[0]}."
        )
    if not np.issubdtype(bundle.input_dtype, np.floating):
        raise RuntimeError(f"Model expects float input, got {bundle.input_dtype}.")
    inp = audio_flat.astype(np.float32).reshape(bundle.input_tensor_shape)
    bundle.interpreter.set_tensor(bundle.input_index, inp)
    bundle.interpreter.invoke()
    out = np.asarray(bundle.interpreter.get_tensor(bundle.output_index), dtype=np.float32).reshape(-1)
    if out.size == 0:
        return None, 0.0, (np.array([], dtype=np.float32) if return_probs else None)
    sm = _maybe_softmax(out)
    idx = int(np.argmax(sm))
    score = float(sm[idx])
    probs = np.copy(sm) if return_probs else None
    if idx >= len(bundle.labels):
        return None, score, probs
    return bundle.labels[idx].strip(), score, probs


def _maybe_softmax(logits: np.ndarray) -> np.ndarray:
    logits = logits.astype(np.float64)
    if np.all(logits >= 0.0) and np.all(logits <= 1.01) and 0.99 <= np.sum(logits) <= 1.01:
        return logits.astype(np.float32)
    z = logits - np.max(logits)
    e = np.exp(z)
    return (e / np.sum(e)).astype(np.float32)


def play_wav(path: Path | str, device: str = "") -> None:
    if shutil.which("aplay") is None:
        raise FileNotFoundError("aplay not found (alsa-utils).")
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
        raise RuntimeError(f"aplay failed: {err}")


def ignore_labels_normalized(ignore: frozenset[str]) -> frozenset[str]:
    return frozenset(s.strip().lower() for s in ignore)
