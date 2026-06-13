# Lesson 5: Microphone + speaker (Module 5)

## Files

| File | Purpose |
|------|---------|
| **LESSON_5_GUIDE.txt** | Mic/speaker chain + every function + feedback hints |
| **challenge.py** | What you edit (`python3 challenge.py`) |
| **starter.py** | Runs `challenge.py` |
| **reply.wav** *(optional)* | Small factory clip if you prefer not to replay the capture |

## Goal

1. **Record** a short clip from the **microphone** (mono WAV).  
2. See a simple **“how loud”** number (**peak 0–1**) from the file.  
3. **Play** something back through the **speaker**—usually the **same recording**, or **`reply.wav`** / system demo if feedback is a problem.

## What you learn

- Capture is **time-based** (seconds of audio in one file).  
- **Noise and echo** are normal in a room.  
- **Mic + speaker** together can **feedback**—volume, aim, and what you play back all matter.

## What you change

In **challenge.py**:

1. **`INPUT_DEVICE`** / **`OUTPUT_DEVICE`** — often start as `""`; set **`plughw:CARD,DEVICE`** from `arecord -l` / `aplay -l` if needed.  
2. **`student_flow()`** — wire `require_tools`, `record_wav`, `rough_peak_level`, `play_wav` (see comments in file).

## Run

```bash
cd ~/lessons/lesson05_mic_speaker
# or: cd ~/Voicedevice/lessons/lesson05_mic_speaker
python3 challenge.py
```

## Needs on the Pi

- **`arecord`** and **`aplay`** (e.g. package **alsa-utils**).  
- User in **`audio`** group on some images: `groups`

## Output file

- **`capture_lesson5.wav`** is written next to `challenge.py` (safe to delete between runs).
