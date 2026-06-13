# Lesson 1: Lights and buzzer (Module 1)

## Files

| File | Purpose |
|------|---------|
| **LESSON_1_GUIDE.txt** | Basics + passive buzzer + every function + hints |
| **challenge.py** | What you edit (`python3 challenge.py`) |
| **starter.py** | Runs `challenge.py` |

## Goal

1. Red LED **on** → **wait** (~3 s) → **off**.  
2. **Passive buzzer:** two **short** tones, one **long** tone (PWM pitch), then silence.

## Buzzer note (important)

This kit uses a **passive** buzzer: sound is made with **PWM** (`passive_tone`) at a **frequency** in Hz — not by holding the pin steady HIGH like an active buzzer.

## What you change

In **challenge.py**:

1. `LED_PIN`, `ON_STATE_KEYWORD`  
2. `BUZZER_PIN` (and optionally `BUZZER_FREQ_HZ`, default 2500)  
3. `student_flow()` — LED helpers first, then `setup_buzzer(BUZZER_PIN)`, then `passive_tone(...)` × 3 with `wait_ms` gaps (see comments in file).

## Run

```bash
cd ~/lessons/lesson01_led_basics
python3 challenge.py
```

## Success

- LED on ~3 s, then off.  
- Two short beeps, one long beep (PWM), then quiet.  
- `Cleanup complete.` after run or Ctrl+C.
