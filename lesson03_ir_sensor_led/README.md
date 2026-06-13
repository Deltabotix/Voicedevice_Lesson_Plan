# Lesson 3: IR sensor + red LED (Module 3)

## Files

| File | Purpose |
|------|---------|
| **LESSON_3_GUIDE.txt** | Input vs output + every function + hints |
| **challenge.py** | What you edit (`python3 challenge.py`) |
| **starter.py** | Runs `challenge.py` |

## Goal

1. Read the **IR sensor** in a **loop** (polling).  
2. Use a simple rule: **obstacle** vs **clear** (pin HIGH vs LOW — you choose which means obstacle).  
3. Drive the **red LED** **on** or **blink** when the rule says something is in front; **off** when clear.

## What you learn

- **Input** pin (sensor) vs **output** pin (LED).  
- Real sensors can be **noisy**; polling with a small delay is normal.  
- Wrong **IR_OBSTACLE_KEYWORD** looks like a “broken” sensor — flip and retest.

## What you change

In **challenge.py**:

1. `ON_STATE_KEYWORD` for the LED.  
2. `IR_PIN` — BCM for the IR module output.  
3. `IR_OBSTACLE_KEYWORD` — `"HIGH"` or `"LOW"` when an object is detected.  
4. `student_flow()` — setup, then a `for`/`while` loop with `obstacle_present()`, `led_on` / `led_off`, `wait_ms`.

`LED_PIN` is **26** on this kit (fixed in file).

## Run

```bash
cd ~/lessons/lesson03_ir_sensor_led
# or: cd ~/Voicedevice/lessons/lesson03_ir_sensor_led
python3 challenge.py
```

## Success

- LED behavior clearly follows **hand in front** vs **clear**.  
- `Cleanup complete.` after run or Ctrl+C.
