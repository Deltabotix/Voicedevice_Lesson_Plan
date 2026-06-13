# Lesson 6: LED via prompt engineering (Module 6)

## Files

| File | Purpose |
|------|---------|
| **LESSON_6_GUIDE.txt** | Prompt + GPIO + every function + hints |
| **challenge.py** | Edit `PROMPT_TEMPLATE`, `TEST_PHRASES`, `student_flow()` |
| **starter.py** | Runs `challenge.py` |

## Goal

Send **short written lines** through a **Groq** call using **`PROMPT_TEMPLATE`**. The model returns **LED_ON**, **LED_OFF**, or **NONE**. Students **change the prompt** and **re-run** to see which phrases control the LED and which should do nothing.

## What you learn

Instructions to the model are **engineering**: you must say what each answer **means** and what the program does next. The LED is the **visible sandbox**.

## Requirements

- **Raspberry Pi** + **GPIO** (red LED on **BCM 26** in this file).  
- **Internet** + **your own Groq API key** in a `.env` file (`GROQ_API_KEY=gsk_...` from [console.groq.com](https://console.groq.com)). Lesson folder or `~/lessons/.env`.
- Python packages: **`groq`**, **`python-dotenv`**. If you see “groq package is not installed”, run **`python3 -m pip install -r requirements.txt`** from this folder (or **`python3 -m pip install groq python-dotenv`**) using the **same** `python3` you use to run the script.

## What you change

In **`challenge.py`**:

1. **`ON_STATE_KEYWORD`**  
2. **`PROMPT_TEMPLATE`** — must include **`{utterance}`**  
3. **`TEST_PHRASES`** — list of strings  
4. **`student_flow()`** — see comments in file (`ensure_prompt_lab_ready`, LED setup, loop)

## Run

```bash
cd ~/lessons/lesson06_led_prompt
# or: cd ~/Voicedevice/lessons/lesson06_led_prompt
export GROQ_API_KEY=...   # if needed
python3 challenge.py
```

## Success

Printed **`phrase -> LED_ON|LED_OFF|NONE`** matches what you expect for most test lines; you can explain one **failure** and how you would tighten the prompt.
