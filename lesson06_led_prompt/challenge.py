"""
Lesson 6 challenge — LED via prompt engineering (Module 6).
Uses Groq (same family as the main VoiceKit). Students edit the prompt template and test phrases.

Edit: ON_STATE_KEYWORD, PROMPT_TEMPLATE, TEST_PHRASES, student_flow().
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import RPi.GPIO as GPIO

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

# Red LED (this kit: BCM 26)
LED_PIN = 26

# TODO: "HIGH" or "LOW" for LED on
ON_STATE_KEYWORD = ""

ON_STATE = None

# TODO: Edit this whole string. Must include "{utterance}" where the user line goes.
# The model must answer with exactly one token: LED_ON, LED_OFF, or NONE.
PROMPT_TEMPLATE = """
You are a strict classifier for a red LED on a Raspberry Pi.

Rules:
- If the user wants the LED turned ON or lit, reply exactly: LED_ON
- If they want it OFF or dark, reply exactly: LED_OFF
- If they are not asking to change the LED (questions, chat, other topics), reply exactly: NONE

User said: "{utterance}"

Reply with exactly one word: LED_ON, LED_OFF, or NONE
""".strip()

# TODO: Add lines people will try (polite, blunt, trick questions)
TEST_PHRASES = []


def student_flow():
    # ensure_prompt_lab_ready()
    # set_on_state(ON_STATE_KEYWORD)
    # setup_led(1LED_PIN)
    # led_off()
    #
    # for phrase in TEST_PHRASES:
    #     label = classify_led_intent(phrase)
    #     print(f"{phrase!r} -> {label}")
    #     apply_led_label(label)
    #     time.sleep(0.4)
    pass


def run_with_guard():
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
            GPIO.cleanup()
        except Exception:
            pass
        print("Cleanup complete.")


def main():
    run_with_guard()


def set_on_state(keyword: str) -> None:
    global ON_STATE
    k = (keyword or "").strip().upper()
    if k == "HIGH":
        ON_STATE = GPIO.HIGH
        return
    if k == "LOW":
        ON_STATE = GPIO.LOW
        return
    raise ValueError('ON_STATE_KEYWORD must be "HIGH" or "LOW".')


def setup_led(pin: int) -> None:
    if ON_STATE is None:
        raise RuntimeError("Call set_on_state() before setup_led().")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)


def led_on() -> None:
    if ON_STATE is None:
        raise RuntimeError("Call set_on_state() before led_on().")
    GPIO.output(LED_PIN, ON_STATE)


def led_off() -> None:
    if ON_STATE is None:
        return
    off = GPIO.LOW if ON_STATE == GPIO.HIGH else GPIO.HIGH
    GPIO.output(LED_PIN, off)


def led_off_safe() -> None:
    if ON_STATE is None:
        return
    try:
        led_off()
    except Exception:
        pass


def print_groq_setup_note() -> None:
    if GROQ_API_KEY:
        where = f" ({_GROQ_ENV_PATH})" if _GROQ_ENV_PATH else ""
        print(f"Groq API key loaded{where}.")
    else:
        print("(No Groq key yet — add GROQ_API_KEY to a .env file; see LESSON_6_GUIDE.txt.)")


def ensure_prompt_lab_ready() -> None:
    if not TEST_PHRASES:
        raise ValueError("Add at least one string to TEST_PHRASES.")
    if "{utterance}" not in PROMPT_TEMPLATE:
        raise ValueError('PROMPT_TEMPLATE must include "{utterance}".')
    groq_env.require_groq_key(_LESSON_DIR)


def classify_led_intent(utterance: str) -> str:
    """Send utterance through PROMPT_TEMPLATE; return LED_ON | LED_OFF | NONE."""
    if Groq is None:
        raise RuntimeError(
            "The groq package is not installed for this Python. On the Pi run:\n"
            "  pip3 install groq python-dotenv\n"
            "or from this lesson folder:\n"
            "  pip3 install -r requirements.txt\n"
            "(Use the same pip/python as `python3 challenge.py` — e.g. `python3 -m pip install groq`.)"
        )
    api_key = groq_env.require_groq_key(_LESSON_DIR)
    if "{utterance}" not in PROMPT_TEMPLATE:
        raise ValueError('PROMPT_TEMPLATE must contain the placeholder "{utterance}".')

    prompt = PROMPT_TEMPLATE.format(utterance=utterance.strip())
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=20,
    )
    raw = (resp.choices[0].message.content or "").strip()
    return normalize_led_label(raw)


def normalize_led_label(raw: str) -> str:
    """Map messy model text to one of LED_ON, LED_OFF, NONE."""
    s = raw.strip().upper()
    s = re.sub(r"```[A-Z]*", "", s)
    s = s.replace("`", "").strip()
    for line in s.splitlines():
        line = line.strip()
        for token in ("LED_ON", "LED_OFF", "NONE"):
            if line == token or line.startswith(token + " ") or line.startswith(token + "."):
                return token
    for token in ("LED_ON", "LED_OFF", "NONE"):
        if re.search(rf"\b{token}\b", s):
            return token
    return "NONE"


def apply_led_label(label: str) -> None:
    if label == "LED_ON":
        led_on()
    elif label == "LED_OFF":
        led_off()
    elif label == "NONE":
        pass
    else:
        raise ValueError(f"Unknown label: {label}")


if __name__ == "__main__":
    main()
