import time

import RPi.GPIO as GPIO

# Kit wiring: MOSFET gate on BCM 12 (do not change)
_STRIP_PIN = 12
_strip_pwm = None


def prepare_strip() -> None:
    global _strip_pwm
    GPIO.setwarnings(False)
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    GPIO.setup(_STRIP_PIN, GPIO.OUT)
    _strip_pwm = GPIO.PWM(_STRIP_PIN, 1000)
    _strip_pwm.start(0.0)
    print("Strip ready (off)")


def set_brightness(percent: float) -> None:
    if _strip_pwm is None:
        raise RuntimeError("Call prepare_strip() first.")
    p = max(0.0, min(100.0, float(percent)))
    _strip_pwm.ChangeDutyCycle(p)
    print(f"Strip brightness {p:.0f}%")


def fade_brightness(
    start_percent: float,
    end_percent: float,
    step: float = 10.0,
    pause_ms: int = 100,
) -> None:
    if _strip_pwm is None:
        raise RuntimeError("Call prepare_strip() first.")
    if step <= 0:
        raise ValueError("step must be positive.")
    a, b = float(start_percent), float(end_percent)
    if abs(a - b) < 1e-6:
        set_brightness(a)
        return
    if a <= b:
        levels: list[float] = []
        x = a
        while x < b - 1e-6:
            levels.append(x)
            x += step
        levels.append(b)
    else:
        levels = []
        x = a
        while x > b + 1e-6:
            levels.append(x)
            x -= step
        levels.append(b)
    for level in levels:
        set_brightness(level)
        time.sleep(pause_ms / 1000.0)


def pause(seconds: int) -> None:
    if seconds < 0:
        raise ValueError("Pause time cannot be negative.")
    time.sleep(seconds)


def pause_ms(milliseconds: int) -> None:
    if milliseconds < 0:
        raise ValueError("Pause time cannot be negative.")
    time.sleep(milliseconds / 1000.0)


def _stop_strip_pwm() -> None:
    global _strip_pwm
    if _strip_pwm is not None:
        try:
            _strip_pwm.ChangeDutyCycle(0)
            _strip_pwm.stop()
        except Exception:
            pass
        _strip_pwm = None


def cleanup() -> None:
    _stop_strip_pwm()
    try:
        GPIO.cleanup()
    except Exception:
        pass
