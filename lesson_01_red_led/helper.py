import time

import RPi.GPIO as GPIO

_led_pin: int | None = None
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
    if not isinstance(pin, int):
        raise ValueError("LED_PIN must be a whole number (BCM pin).")
    if _on_level is None:
        raise RuntimeError("Call pick_how_led_turns_on() before prepare_led().")
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    _led_pin = pin


def light_on() -> None:
    if _led_pin is None or _on_level is None:
        raise RuntimeError("Prepare the LED first.")
    GPIO.output(_led_pin, _on_level)
    print("LED is ON")


def light_off() -> None:
    if _led_pin is None or _on_level is None:
        raise RuntimeError("Prepare the LED first.")
    off_level = GPIO.LOW if _on_level == GPIO.HIGH else GPIO.HIGH
    GPIO.output(_led_pin, off_level)
    print("LED is OFF")


def pause(seconds: int) -> None:
    if seconds < 0:
        raise ValueError("Pause time cannot be negative.")
    time.sleep(seconds)


def cleanup() -> None:
    if _led_pin is None:
        return
    try:
        off_level = GPIO.LOW if _on_level == GPIO.HIGH else GPIO.HIGH
        GPIO.output(_led_pin, off_level)
    except Exception:
        pass
    try:
        GPIO.cleanup()
    except Exception:
        pass
