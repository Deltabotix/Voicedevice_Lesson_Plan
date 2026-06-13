# Lesson 10: Voice beat sequencer (Teachable Machine — Module 10)

## Goal

Train Teachable Machine with **one class per hit** (`drum`, `snare1`, …) plus **background** and a **`stop`** class. **Phase A:** speak a sequence of hits, then say **`stop`** to finish recording. **Phase B:** the kit **loops** that sequence on the speaker; optional **LED flash** on each hit. Say **`stop`** again in the gap **between full loops** to exit cleanly (or use Ctrl+C).

## Files

| File | Role |
|------|------|
| **LESSON_10_GUIDE.txt** | Theory + fill-in |
| **challenge.py** | `BEAT_LABEL_TO_WAV`, `STOP_CLASS_NAME`, timing, LED |
| **starter.py** | Runs `challenge.py` |
| **requirements.txt** | Same stack as Lesson 9 |
| **sounds/beat_kit/** | Your ~1 s WAVs per voice (see `README.txt` there) |
| **`../tm_audio_runtime.py`** | Shared TM inference |

## Teachable Machine

- Class names should match **dictionary keys** in `BEAT_LABEL_TO_WAV` (e.g. `drum`, `snare1`, `stop`).
- Export **TensorFlow Lite** + **`labels.txt`** into this folder (Lesson 8 transfer steps apply).

## Run

```bash
cd ~/Voicedevice/lessons/lesson10_voice_beat_sequencer
python3 -m pip install -r requirements.txt
python3 challenge.py
```

## Success

You record a short spoken pattern, hear it **repeat as a loop**, and **`stop`** ends playback without needing a physical button (button is optional in hardware extensions).
