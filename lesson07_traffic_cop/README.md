# Lesson 7: Traffic cop (Module 7)

## Goal

Classify each **sentence** into **`CONTROL`** (user wants hardware to move) or **`GENERAL`** (normal talk). Students edit **`PROMPT_TEMPLATE`** and **`TEST_PHRASES`**, run the script, and count how lines sort. Optional: **blink the LED** when the answer is **CONTROL** so the split is visible.

## Files

| File | Purpose |
|------|---------|
| **LESSON_7_GUIDE.txt** | Theory + every helper |
| **challenge.py** | `PROMPT_TEMPLATE`, `TEST_PHRASES`, `BLINK_ON_CONTROL`, `student_flow()` |
| **starter.py** | Runs `challenge.py` |
| **requirements.txt** | `groq`, `python-dotenv`, `RPi.GPIO` (GPIO no-op off-Pi if import fails) |

## Requirements

- **Your own Groq API key** in `.env` (see Lesson 6 README).
- **Raspberry Pi** for LED blink; classifier itself can be tested on any machine with `groq` installed.

## Run

```bash
cd ~/Voicedevice/lessons/lesson07_traffic_cop
python3 -m pip install -r requirements.txt
python3 challenge.py
```

## Success

Hardware-like lines → **`CONTROL`**; chat/questions → **`GENERAL`** for most of your test list; optional LED blinks only on **CONTROL**.
