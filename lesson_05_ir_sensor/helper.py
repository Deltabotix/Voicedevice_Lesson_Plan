import time

import RPi.GPIO as GPIO

_led_pin: int | None = None
_on_level = None
_ir_pin: int | None = None
_blocked_is_high: bool | None = None


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


def pick_when_blocked_is(keyword: str) -> None:
    global _blocked_is_high
    k = (keyword or "").strip().upper()
    if k == "HIGH":
        _blocked_is_high = True
        return
    if k == "LOW":
        _blocked_is_high = False
        return
    raise ValueError('BLOCKED_IS must be "HIGH" or "LOW".')


def prepare_led(pin: int) -> None:
    global _led_pin
    if not isinstance(pin, int):
        raise ValueError("LED_PIN must be a whole number (BCM pin).")
    if _on_level is None:
        raise RuntimeError("Call pick_how_led_turns_on() before prepare_led().")
    GPIO.setwarnings(False)
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    _led_pin = pin


def prepare_ir_sensor(pin: int) -> None:
    global _ir_pin
    if not isinstance(pin, int):
        raise ValueError("IR_PIN must be a whole number (BCM pin).")
    if _blocked_is_high is None:
        raise RuntimeError("Call pick_when_blocked_is() before prepare_ir_sensor().")
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    _ir_pin = pin


def something_nearby() -> bool:
    if _ir_pin is None or _blocked_is_high is None:
        raise RuntimeError("Prepare the IR sensor first.")
    reading = GPIO.input(_ir_pin)
    if _blocked_is_high:
        return reading == GPIO.HIGH
    return reading == GPIO.LOW


def light_on() -> None:
    if _led_pin is None or _on_level is None:
        raise RuntimeError("Prepare the LED first.")
    GPIO.output(_led_pin, _on_level)
    print("LED is ON")


def light_off() -> None:
    if _led_pin is None or _on_level is None:
        raise RuntimeError("Prepare the LED first.")
    off = GPIO.LOW if _on_level == GPIO.HIGH else GPIO.HIGH
    GPIO.output(_led_pin, off)
    print("LED is OFF")


def pause_ms(milliseconds: int) -> None:
    if milliseconds < 0:
        raise ValueError("Pause time cannot be negative.")
    time.sleep(milliseconds / 1000.0)


def cleanup() -> None:
    try:
        light_off()
    except Exception:
        pass
    try:
        GPIO.cleanup()
    except Exception:
        pass
