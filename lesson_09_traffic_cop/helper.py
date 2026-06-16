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

_LESSONS_DIR = Path(__file__).resolve().parent.parent
if str(_LESSONS_DIR) not in sys.path:
    sys.path.insert(0, str(_LESSONS_DIR))

import groq_env

GROQ_MODEL = "llama-3.1-8b-instant"
_LED_PIN: int | None = None
_on_level = None


def pick_how_led_turns_on(keyword: str) -> None:
    global _on_level
    k = (keyword or "").strip().upper()
    if k == "HIGH":
        _on_level = GPIO.HIGH
        return
    if k == "LOW":
        _on_level = GPIO.LOW
        return
    raise ValueError('LED_ON_LEVEL must be "HIGH" or "LOW".')


def prepare_led(pin: int) -> None:
    global _led_pin
    if _on_level is None:
        raise RuntimeError("Call pick_how_led_turns_on() first.")
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    _led_pin = pin


def light_on() -> None:
    if _led_pin is None or _on_level is None:
        return
    GPIO.output(_led_pin, _on_level)


def light_off() -> None:
    if _led_pin is None or _on_level is None:
        return
    off = GPIO.LOW if _on_level == GPIO.HIGH else GPIO.HIGH
    GPIO.output(_led_pin, off)


def check_traffic_lab_ready(test_phrases: list[str], prompt_template: str) -> None:
    if not test_phrases:
        raise ValueError("Add at least one line to TEST_PHRASES.")
    if "{utterance}" not in prompt_template:
        raise ValueError('PROMPT_TEMPLATE must include "{utterance}".')
    groq_env.require_groq_key(Path(__file__).resolve().parent)


def classify_route(utterance: str, prompt_template: str) -> str:
    if Groq is None:
        raise RuntimeError("groq package missing — use the kit voicekit venv.")
    api_key = groq_env.require_groq_key(Path(__file__).resolve().parent)
    prompt = prompt_template.format(utterance=utterance.strip())
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=16,
    )
    raw = (resp.choices[0].message.content or "").strip()
    return _normalize_tag(raw)


def blink_on_control(
    tag: str,
    enabled: bool = True,
    pulses: int = 2,
    on_sec: float = 0.09,
    off_sec: float = 0.08,
) -> None:
    if not enabled or tag != "CONTROL" or _led_pin is None or _on_level is None:
        return
    for _ in range(max(1, pulses)):
        light_on()
        time.sleep(on_sec)
        light_off()
        time.sleep(off_sec)
    print("CONTROL — LED blink")


def pause(seconds: float) -> None:
    time.sleep(max(0.0, seconds))


def _normalize_tag(raw: str) -> str:
    s = raw.strip().upper()
    s = re.sub(r"```[A-Z]*", "", s).replace("`", "").strip()
    for line in s.splitlines():
        line = line.strip()
        for token in ("CONTROL", "GENERAL"):
            if line == token or line.startswith(token + " "):
                return token
    for token in ("CONTROL", "GENERAL"):
        if re.search(rf"\b{token}\b", s):
            return token
    return "GENERAL"


def cleanup() -> None:
    if _led_pin is None:
        return
    try:
        light_off()
    except Exception:
        pass
    try:
        GPIO.cleanup()
    except Exception:
        pass
