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

**Two different `run.sh` files on the kit**

| Path | Purpose |
|------|---------|
| `~/lessons/run` or `~/lessons/run.sh` | **Lessons** — `./run 1`, `./run 8`, … |
| `~/run.sh` | **Voice assistant** — started by captive portal (not lessons) |

## Commands

| Script | Purpose |
|--------|---------|
| `./run N` or `./run.sh N` | Run lesson N (`run.sh` is the same as `run`) |
| `./reset N` | Restore `my_program.py` for lesson N from Git |
| `./reset --all` | Restore all tracked files |
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

## Teachable Machine

Record on the Pi → one **zip per class** → upload in TM → export **tflite** back.

See **[TM_AUDIO_WORKFLOW.txt](TM_AUDIO_WORKFLOW.txt)** and **`tm_pack_class.py`**.

| Folder | Topic | Run |
|--------|--------|-----|
| `lesson08_barnyard_tm` | Barnyard soundboard | `./run lesson08_barnyard_tm` |
| `lesson09_clubhouse_knock` | Secret knock | `./run lesson09_clubhouse_knock` |
| `lesson10_voice_beat_sequencer` | Voice beat loop | `./run lesson10_voice_beat_sequencer` |

Shared: **`tm_audio_runtime.py`**. On the Pi after training: **`model.tflite`** + **`labels.txt`** in each TM lesson folder.

## Groq (lessons 8–9)

Key is saved when you set up Wi‑Fi on the kit (`/home/voicedevice/.env`). If Groq fails, ask your teacher or re-run kit setup.

## Docs

- [LESSON_CONVENTIONS.md](LESSON_CONVENTIONS.md) — folder layout, guides, reset policy
- [CURRICULUM_MODULES_1_TO_10.txt](CURRICULUM_MODULES_1_TO_10.txt) — module overview

## Reset policy

```bash
./reset 1
```

## Kit maintainers

- **`requirements.txt`** — extra packages for lessons (e.g. `sounddevice` for 8–10) added into voicekit venv
- **`image_setup_venv.sh`** — `pip install -r requirements.txt` into `/opt/voicedevice/voicekit_v2/venv`
- Override venv path: `LESSONS_VENV=/path/to/venv ./run 1`
