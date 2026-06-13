# Lesson 2: MOSFET + 12 V strip + servo (Module 2)

## Files

| File | Purpose |
|------|---------|
| **LESSON_2_GUIDE.txt** | Short theory + every function + hints |
| **challenge.py** | What you edit (`python3 challenge.py`) |
| **starter.py** | Runs `challenge.py` |

## Goal

1. Move the **servo** through **three clear angles** (e.g. left / middle / right) with **short pauses**.  
2. Change **12 V LED strip** brightness through **several steps** or a **simple ramp** (MOSFET PWM on **BCM 12**), then finish with the strip **off** (0%).

## Hardware reminder

- **12 V** for the strip comes from the **kit adapter**, not from the Pi GPIO.  
- The Pi drives **pin 12** (PWM) → **MOSFET** → strip.  
- **Servo** signal: one of **BCM 4, 5, 6, 17, 27** (set `SERVO_PIN` to match your wiring).

## What you change

In **challenge.py`:

1. `SERVO_PIN` — integer from `{4, 5, 6, 17, 27}` per your diagram.  
2. `student_flow()` — `setup_mosfet_strip`, `setup_servo(SERVO_PIN)`, then `set_servo_angle` / `wait_seconds`, then `set_strip_brightness_percent` and/or `ramp_strip_brightness`, ending with **`set_strip_brightness_percent(0)`**.

`MOSFET_PIN` is **12** and is not a student TODO.

## Run

```bash
cd ~/lessons/lesson02_mosfet_servo
# or: cd ~/Voicedevice/lessons/lesson02_mosfet_servo
python3 challenge.py
```

## Success

- Three servo positions with pauses.  
- Strip brightness changes visibly, then **0%** at the end.  
- `Cleanup complete.` after run or Ctrl+C.
