# Voice Device — Lessons

Hands-on coding lessons for the Voice Device kit (Raspberry Pi). Students edit **`my_program.py`** in each lesson folder; kit code lives in **`helper.py`**.

## Quick start (on the Pi)

```bash
git clone https://github.com/YOUR_ORG/voicedevice-lessons.git ~/lessons
cd ~/lessons
chmod +x run run.sh reset.sh reset_lesson.sh update.sh setup_venv.sh
./setup_venv.sh
./run 1
```

See **[GETTING_STARTED_ON_THE_PI.txt](GETTING_STARTED_ON_THE_PI.txt)** for full details.

## Commands

| Script | Purpose |
|--------|---------|
| `./run N` or `./run.sh N` | Run lesson N (uses `venv`, pauses Wi‑Fi captive portal) |
| `./reset.sh N` | Restore `my_program.py` for lesson N from Git |
| `./reset.sh --all` | Restore all tracked files |
| `./update.sh` | `git pull` latest lessons |

## Lesson 1 (template)

New-style folder: **`lesson_01_red_led/`** — `my_program.py`, `helper.py`, `run.py`, guide.

Legacy folders (`lesson01_led_basics`, …) still use `challenge.py` / `starter.py` until migrated.

## Groq (lessons 6–7)

1. Create a key at [console.groq.com](https://console.groq.com)
2. Copy `.env.example` → `.env` and set `GROQ_API_KEY=`

## Teachable Machine (lessons 8–10)

Export **TensorFlow Lite** + **`labels.txt`** into the lesson folder (not in this repo).

## Docs

- [LESSON_CONVENTIONS.md](LESSON_CONVENTIONS.md) — folder layout, guides, reset policy
- [CURRICULUM_MODULES_1_TO_10.txt](CURRICULUM_MODULES_1_TO_10.txt) — module overview

## Reset policy

No local starter copies. Reset always comes from Git:

```bash
./reset.sh 1
```
