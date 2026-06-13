"""
Lesson 7 challenge — Traffic cop: CONTROL vs GENERAL (Module 7).

Uses Groq. The model must reply with exactly one word: CONTROL or GENERAL.
Optional: blink the kit LED when the tag is CONTROL so the room sees the split.

Edit: ON_STATE_KEYWORD, PROMPT_TEMPLATE, TEST_PHRASES, BLINK_ON_CONTROL, student_flow().
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None  # type: ignore

try:
    from groq import Groq
except ImportError:
    Groq = None  # type: ignore

_LESSON_DIR = Path(__file__).resolve().parent
if str(_LESSON_DIR.parent) not in sys.path:
    sys.path.insert(0, str(_LESSON_DIR.parent))

import groq_env

GROQ_API_KEY, _GROQ_ENV_PATH = groq_env.load_groq_config(_LESSON_DIR)
GROQ_MODEL = "llama-3.1-8b-instant"

# Red LED (kit: BCM 26) — optional blink when tag is CONTROL
LED_PIN = 26
# TODO: "HIGH" or "LOW" for LED on (only used if BLINK_ON_CONTROL and GPIO available)
ON_STATE_KEYWORD = ""

# Blink pattern when classification is CONTROL (so the class sees hardware-path traffic)
BLINK_ON_CONTROL = True
BLINK_PULSES = 2
BLINK_ON_SEC = 0.09
BLINK_OFF_SEC = 0.08

ON_STATE = None

# TODO: Must include "{utterance}". Model must answer with exactly CONTROL or GENERAL.
PROMPT_TEMPLATE = """
You are a traffic cop for a voice-controlled Raspberry Pi kit.

Decide whether the user sentence is asking to CONTROL physical hardware on the device
(motors, LEDs, lights, buzzer, servo, strip brightness, sensors as commands, "turn on…", "set angle…"),
or is GENERAL conversation (questions, facts, chat, math, weather, jokes) that should NOT
route to hardware actuators.

Reply with exactly one word:
- CONTROL — if they want hardware to do something or report a hardware command.
- GENERAL — for normal talk, questions, or anything that is not a direct hardware command.

User said: "{utterance}"

Reply with exactly one word: CONTROL or GENERAL
""".strip()

# TODO: Sample lines: hardware-ish vs chat (polite, blunt, edge cases)
TEST_PHRASES: list[str] = []


def student_flow() -> None:
    # Default (see LESSON_7_GUIDE.txt):
    # print_groq_setup_note()
    # ensure_traffic_lab_ready()
    # set_on_state(ON_STATE_KEYWORD)
    # setup_led(LED_PIN)
    # led_off()
    # for phrase in TEST_PHRASES:
    #     tag = classify_traffic(phrase)
    #     print(f"{phrase!r} -> {tag}")
    #     if BLINK_ON_CONTROL and tag == "CONTROL":
    #         blink_control_led()
    #     time.sleep(0.35)
    pass


def run_with_guard() -> None:
    try:
        student_flow()
    except ValueError as e:
        print(f"Input error: {e}")
    except RuntimeError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        try:
            led_off_safe()
        except Exception:
            pass
        try:
            if GPIO is not None:
                GPIO.cleanup()
        except Exception:
            pass
        print("Cleanup complete.")


def main() -> None:
    run_with_guard()


def set_on_state(keyword: str) -> None:
    global ON_STATE
    if GPIO is None:
        ON_STATE = None
        return
    k = (keyword or "").strip().upper()
    if k == "HIGH":
        ON_STATE = GPIO.HIGH
        return
    if k == "LOW":
        ON_STATE = GPIO.LOW
        return
    raise ValueError('ON_STATE_KEYWORD must be "HIGH" or "LOW".')


def setup_led(pin: int) -> None:
    if GPIO is None:
        return
    if ON_STATE is None:
        raise RuntimeError("Call set_on_state() before setup_led().")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)


def led_on() -> None:
    if GPIO is None or ON_STATE is None:
        return
    GPIO.output(LED_PIN, ON_STATE)


def led_off() -> None:
    if GPIO is None or ON_STATE is None:
        return
    off = GPIO.LOW if ON_STATE == GPIO.HIGH else GPIO.HIGH
    GPIO.output(LED_PIN, off)


def led_off_safe() -> None:
    try:
        led_off()
    except Exception:
        pass


def blink_control_led() -> None:
    """Short blink train when tag is CONTROL (optional classroom demo)."""
    if not BLINK_ON_CONTROL or GPIO is None or ON_STATE is None:
        return
    for _ in range(max(1, BLINK_PULSES)):
        led_on()
        time.sleep(BLINK_ON_SEC)
        led_off()
        time.sleep(BLINK_OFF_SEC)


def print_groq_setup_note() -> None:
    if GROQ_API_KEY:
        where = f" ({_GROQ_ENV_PATH})" if _GROQ_ENV_PATH else ""
        print(f"Groq API key loaded{where}.")
    else:
        print("(No Groq key yet — add GROQ_API_KEY to a .env file; see LESSON_7_GUIDE.txt.)")


def ensure_traffic_lab_ready() -> None:
    if not TEST_PHRASES:
        raise ValueError("Add at least one string to TEST_PHRASES.")
    if "{utterance}" not in PROMPT_TEMPLATE:
        raise ValueError('PROMPT_TEMPLATE must include "{utterance}".')
    groq_env.require_groq_key(_LESSON_DIR)


def classify_traffic(utterance: str) -> str:
    """Return CONTROL or GENERAL."""
    if Groq is None:
        raise RuntimeError(
            "groq not installed. Run: python3 -m pip install groq python-dotenv"
        )
    api_key = groq_env.require_groq_key(_LESSON_DIR)
    if "{utterance}" not in PROMPT_TEMPLATE:
        raise ValueError('PROMPT_TEMPLATE must contain "{utterance}".')
    prompt = PROMPT_TEMPLATE.format(utterance=utterance.strip())
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=16,
    )
    raw = (resp.choices[0].message.content or "").strip()
    return normalize_traffic_tag(raw)


def normalize_traffic_tag(raw: str) -> str:
    s = raw.strip().upper()
    s = re.sub(r"```[A-Z]*", "", s)
    s = s.replace("`", "").strip()
    for line in s.splitlines():
        line = line.strip()
        for token in ("CONTROL", "GENERAL"):
            if line == token or line.startswith(token + " ") or line.startswith(token + "."):
                return token
    for token in ("CONTROL", "GENERAL"):
        if re.search(rf"\b{token}\b", s):
            return token
    return "GENERAL"


if __name__ == "__main__":
    main()