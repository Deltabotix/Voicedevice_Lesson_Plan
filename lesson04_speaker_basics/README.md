# Lesson 4: Speaker (Module 4)

## Files

| File | Purpose |
|------|---------|
| **LESSON_4_GUIDE.txt** | Audio chain + every function + hints |
| **challenge.py** | What you edit (`python3 challenge.py`) |
| **starter.py** | Runs `challenge.py` |
| **test.wav** *(optional)* | Drop a small WAV here if the Pi has no system demo files |

## Goal

Play a **test WAV** through the kit **speaker path** using the lesson’s **`aplay`** helper. If it fails, use the printed **checklist** (device, volume, wiring, correct card, file format).

## What you learn

Sound is a **chain**: file → player (`aplay`) → ALSA device → amp → speaker. Any step can fail; this lesson gives a **baseline** before mic + voice lessons.

## What you change

In **challenge.py**:

1. **`AUDIO_DEVICE`** — often start as `""` (default). If silent, set e.g. `"plughw:0,0"` after `aplay -l`.  
2. **`student_flow()`** — e.g. `find_test_audio()` then `play_wav(...)`, or `try_play_wav` + `print_audio_checklist` on failure.

## Run

```bash
cd ~/lessons/lesson04_speaker_basics
# or: cd ~/Voicedevice/lessons/lesson04_speaker_basics
python3 challenge.py
```

## Success

- You hear the test clip **or** you deliberately walk the **checklist** and document the next fix (good for class demos too).

## Needs on the Pi

- **`aplay`** (usually from package **alsa-utils**): `which aplay`
