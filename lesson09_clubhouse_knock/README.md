# Lesson 9: Secret clubhouse knock (Teachable Machine — Module 9)

## Goal

Train a few **password** sounds (knocks, whistles, words) plus **background** in [Teachable Machine](https://teachablemachine.withgoogle.com/), export **TensorFlow Lite** + **`labels.txt`**. On the Pi: if the winning class is in **`UNLOCK_LABELS`** with high confidence → **OK LED** + success WAV; if another class is confident (intruder) → **NO LED** + deny WAV. Same audio stack as Lesson 8 (`tm_audio_runtime`).

## Files

| File | Role |
|------|------|
| **LESSON_9_GUIDE.txt** | Theory + fill-in list |
| **challenge.py** | `UNLOCK_LABELS`, thresholds, GPIO pins, WAV paths |
| **starter.py** | Runs `challenge.py` |
| **requirements.txt** | `tflite-runtime`, `numpy`, `sounddevice`, `RPi.GPIO` |
| **`../tm_audio_runtime.py`** | Shared TM inference helpers (do not move without updating `sys.path`) |

## Setup

1. Copy **`model.tflite`** (or `soundclassifier_with_metadata.tflite`) and **`labels.txt`** into this folder (see Lesson 8 README for `scp`).
2. `python3 -m pip install -r requirements.txt`
3. Edit **`UNLOCK_LABELS`** to match your TM **class name(s)** exactly.
4. Set **`SUCCESS_WAV`** / **`DENY_WAV`** (system ALSA demos are fine for testing).
5. Match **`LED_OK_PIN`** / **`LED_NO_PIN`** and **`ON_STATE_KEYWORD`** to your kit.

## Run

```bash
cd ~/Voicedevice/lessons/lesson09_clubhouse_knock
python3 challenge.py
```

## Success

Password sound → green/blue “OK” behavior + success tone; random confident word → red “no” + deny tone; background stays quiet.
