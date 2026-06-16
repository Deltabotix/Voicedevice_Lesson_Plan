#!/usr/bin/env python3
"""
Record a Teachable Machine audio class on the Pi and pack a class zip.

Teachable Machine expects one zip per class containing:
  - recording.webm   (~20 s of audio, many short samples in one take)
  - samples.json     (segment times + frequencyFrames per sample)

Usage (from ~/lessons):
  python3 tm_pack_class.py background
  python3 tm_pack_class.py cat

During recording, make your sound about once per second for ~20 seconds
(e.g. say "cat" ... "cat" ... or leave quiet for background).

Copy each *.zip to your laptop and upload it into the matching TM class.
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
import wave
import zipfile
from pathlib import Path

LESSONS_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = LESSONS_DIR / "tm_recordings"
NUM_SAMPLES = 20
RECORD_SECONDS = 21
SAMPLE_RATE = 44100  # matches Teachable Machine browser captures
N_FRAMES = 43
N_BINS = 232


def _require(cmd: str) -> None:
    if shutil.which(cmd) is None:
        raise RuntimeError(f"Missing '{cmd}' on PATH. Install it on the Pi image.")


def record_wav(out_path: Path, seconds: int, device: str = "") -> None:
    _require("arecord")
    cmd = [
        "arecord", "-q",
        "-f", "S16_LE",
        "-r", str(SAMPLE_RATE),
        "-c", "1",
        "-d", str(seconds),
        str(out_path),
    ]
    if device.strip():
        cmd[1:1] = ["-D", device.strip()]
    print(f"Recording {seconds}s → speak/make your sound about once per second …")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "arecord failed").strip())


def wav_to_webm(wav_path: Path, webm_path: Path) -> None:
    _require("ffmpeg")
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(wav_path),
        "-c:a", "libopus",
        str(webm_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or "ffmpeg failed").strip())


def read_wav_mono(path: Path) -> tuple[list[float], int]:
    with wave.open(str(path), "rb") as w:
        rate = w.getframerate()
        raw = w.readframes(w.getnframes())
        width = w.getsampwidth()
    if width != 2:
        raise RuntimeError("Expected 16-bit WAV from arecord.")
    import struct

    samples = [struct.unpack_from("<h", raw, i)[0] / 32768.0 for i in range(0, len(raw) - 1, 2)]
    return samples, rate


def frequency_frames(segment: list[float], sample_rate: int) -> list[list[float]]:
    """Approximate TM frequencyFrames (43 × 232 dB FFT values per sample)."""
    if not segment:
        return [[-100.0] * N_BINS for _ in range(N_FRAMES)]

    try:
        import numpy as np
    except ImportError:
        return [[-100.0] * N_BINS for _ in range(N_FRAMES)]

    arr = np.array(segment, dtype=np.float64)
    frame_len = max(1, len(arr) // N_FRAMES)
    frames: list[list[float]] = []
    for i in range(N_FRAMES):
        chunk = arr[i * frame_len : (i + 1) * frame_len]
        if len(chunk) < 8:
            frames.append([-100.0] * N_BINS)
            continue
        spectrum = np.abs(np.fft.rfft(chunk))
        if len(spectrum) < N_BINS:
            spectrum = np.pad(spectrum, (0, N_BINS - len(spectrum)))
        else:
            spectrum = spectrum[:N_BINS]
        db = 20.0 * np.log10(np.maximum(spectrum, 1e-10))
        frames.append([float(x) for x in db])
    return frames


def build_samples_json(samples: list[float], sample_rate: int, duration: float) -> list[dict]:
    step = duration / NUM_SAMPLES
    out: list[dict] = []
    for i in range(NUM_SAMPLES):
        start_t = i * step
        end_t = duration if i == NUM_SAMPLES - 1 else (i + 1) * step
        i0 = int(start_t * sample_rate)
        i1 = int(end_t * sample_rate)
        segment = samples[i0:i1]
        out.append({
            "startTime": start_t,
            "endTime": end_t,
            "recordingDuration": duration,
            "frequencyFrames": frequency_frames(segment, sample_rate),
        })
    return out


def pack_class(class_name: str, device: str = "") -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in class_name.strip())
    if not safe:
        raise ValueError("Class name cannot be empty.")

    work = OUTPUT_DIR / safe
    work.mkdir(parents=True, exist_ok=True)
    wav_path = work / "recording.wav"
    webm_path = work / "recording.webm"
    json_path = work / "samples.json"
    zip_path = OUTPUT_DIR / f"{safe}.zip"

    record_wav(wav_path, RECORD_SECONDS, device)
    wav_to_webm(wav_path, webm_path)

    mono, rate = read_wav_mono(wav_path)
    duration = len(mono) / float(rate)
    samples = build_samples_json(mono, rate, duration)
    json_path.write_text(json.dumps(samples, indent=2), encoding="utf-8")

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(webm_path, "recording.webm")
        zf.write(json_path, "samples.json")

    print(f"Created {zip_path}")
    print(f"  {NUM_SAMPLES} samples in {duration:.2f}s webm + samples.json")
    print("Copy to laptop: scp voicedevice@PI_IP:~/lessons/tm_recordings/*.zip ~/Downloads/")
    return zip_path


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    device = ""
    if "--device" in sys.argv:
        idx = sys.argv.index("--device")
        device = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
    class_name = sys.argv[1]
    if class_name in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    pack_class(class_name, device=device)


if __name__ == "__main__":
    main()
