# Voice Device — Lessons

Hands-on coding lessons for the Voice Device kit (Raspberry Pi). Students edit **`my_program.py`** in each lesson folder; kit code lives in **`helper.py`**.

## On the kit (normal use)

Lessons run with the **same Python venv as voicekit** — already on the Pi:

`/opt/voicedevice/voicekit_v2/venv`

You do **not** create a separate venv or run `pip install`.

```bash
cd ~/lessons
./run 1
```

Get new lesson **code** from GitHub (the venv stays on the Pi — it is not in this repo):

```bash
cd ~/lessons
./update.sh
# or: git pull
```

See **[GETTING_STARTED_ON_THE_PI.txt](GETTING_STARTED_ON_THE_PI.txt)** for full details.

## Commands

| Script | Purpose |
|--------|---------|
| `./run N` or `./run.sh N` | Run lesson N (voicekit venv, pauses Wi‑Fi captive portal) |
| `./reset.sh N` | Restore `my_program.py` for lesson N from Git |
| `./reset.sh --all` | Restore all tracked files |
| `./update.sh` | `git pull` latest lessons |

## New-style lessons (1–9)

| # | Folder | Topic |
|---|--------|--------|
| 1 | `lesson_01_red_led` | Red LED |
| 2 | `lesson_02_buzzer` | Passive buzzer (PWM) |
| 3 | `lesson_03_led_strip` | 12 V strip + MOSFET |
| 4 | `lesson_04_servo` | Servo angles |
| 5 | `lesson_05_ir_sensor` | IR sensor + LED |
| 6 | `lesson_06_speaker` | Speaker / aplay |
| 7 | `lesson_07_mic_speaker` | Mic record + playback |
| 8 | `lesson_08_led_prompt` | Groq → LED (prompt engineering) |
| 9 | `lesson_09_traffic_cop` | Groq CONTROL vs GENERAL |

Legacy folders (`lesson03_ir_sensor_led`, …) still use `challenge.py` until removed.

## Groq (lessons 8–9)

Uses **`groq`** and **`python-dotenv`** from the voicekit venv. Set your key in `.env`:

1. Create a key at [console.groq.com](https://console.groq.com)
2. Copy `.env.example` → `.env` (or use `/opt/voicedevice/.env` on the kit)

## Teachable Machine (lessons 10+)

Export **TensorFlow Lite** + **`labels.txt`** into the lesson folder (not in this repo).

## Docs

- [LESSON_CONVENTIONS.md](LESSON_CONVENTIONS.md) — folder layout, guides, reset policy
- [CURRICULUM_MODULES_1_TO_10.txt](CURRICULUM_MODULES_1_TO_10.txt) — module overview

## Reset policy

```bash
./reset.sh 1
```

## Kit maintainers

- **`requirements.txt`** — extra packages for lessons (e.g. `sounddevice` for 8–10) added into voicekit venv
- **`image_setup_venv.sh`** — `pip install -r requirements.txt` into `/opt/voicedevice/voicekit_v2/venv`
- Override venv path: `LESSONS_VENV=/path/to/venv ./run 1`
