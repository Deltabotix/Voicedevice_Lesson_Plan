# Lesson conventions (follow for every new lesson)

## Folder layout

```
lesson_NN_topic/
  my_program.py   ← students edit ONLY this file
  helper.py       ← kit code (do not edit)
  run.py          ← runner (do not edit)
  LESSON_N_GUIDE.txt
  README.md
```

**No** `my_program.starter.py`, **no** `starter.py`, **no** duplicate challenge.py for students.

## Student entry point

- Function name: **`my_program()`**
- Settings (pins, templates, lists) live at the top of **`my_program.py`**
- Comments **only** inside **`my_program()`** (step hints); nowhere else in student-facing files

## Helper API naming

Use plain English for functions students call from `helper.py`:

- `light_on()` not `led_on()` where possible
- `pause()` not `wait_seconds()`
- `pick_how_led_turns_on()` / `LED_ON_LEVEL` not `ON_STATE_KEYWORD`

## Guides (`LESSON_N_GUIDE.txt`)

Match **Lesson 1** structure:

1. **Understand it** — how it works, key concept, what you will do, real-world use  
2. **Create it** — what you need, files, Steps A–D, how the code works  
3. **Test and improve it** — success checks, troubleshooting, evaluation  
4. **Go further** — extensions  
5. **Reset your file** — Git only (see below)

Tone: beginner-friendly, micro:bit style. No jargon blocks in the guide header.

## Run

From `~/lessons`:

```bash
./run N
```

Uses the kit Python at **`/opt/voicedevice/voicekit_v2/venv`** (same venv as voicekit_v2). Each lesson’s `run.py` is executed with that interpreter.

## Reset (Git only)

Students clone the repo; reset comes from Git, not copied starter files.

One lesson:

```bash
cd ~/lessons
git checkout -- lesson_01_red_led/my_program.py
# or
./reset 1
```

All lessons:

```bash
cd ~/lessons
./reset --all
# or: git checkout -- .
```

To match a release tag: `git fetch --tags && git checkout lessons-v1.0 -- lesson_01_red_led/my_program.py`

## Groq (lessons that need it)

- **No** volunteer PIN, **no** shared kit key, **no** captive-portal Groq flow in lesson docs  
- Students use **their own** `GROQ_API_KEY` in `.env`  
- Load via `groq_env.require_groq_key()` from `lessons/groq_env.py`

## Do not mention in lesson materials

- Volunteer login / volunteer PIN  
- Shared Groq keys from the kit  
- `my_program.starter.py` or local starter copies
