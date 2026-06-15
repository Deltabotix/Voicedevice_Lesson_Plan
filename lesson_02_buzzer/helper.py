import time

import RPi.GPIO as GPIO

_buzzer_pin: int | None = None
_buzzer_pwm = None


def prepare_buzzer(pin: int) -> None:
    global _buzzer_pin
    if not isinstance(pin, int):
        raise ValueError("BUZZER_PIN must be a whole number (BCM pin).")
    GPIO.setwarnings(False)
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    _buzzer_pin = pin


def beep(duration_ms: int, frequency_hz: int = 2500) -> None:
    global _buzzer_pwm
    if _buzzer_pin is None:
        raise RuntimeError("Call prepare_buzzer() first.")
    if duration_ms < 0:
        raise ValueError("Beep length cannot be negative.")
    if frequency_hz < 50 or frequency_hz > 8000:
        raise ValueError("frequency_hz: try 2000–4000 for this buzzer.")

    _stop_pwm()
    _buzzer_pwm = GPIO.PWM(_buzzer_pin, frequency_hz)
    _buzzer_pwm.start(50)
    time.sleep(duration_ms / 1000.0)
    _stop_pwm()
    print(f"Beep ({duration_ms} ms at {frequency_hz} Hz)")


def pause_ms(milliseconds: int) -> None:
    if milliseconds < 0:
        raise ValueError("Pause time cannot be negative.")
    time.sleep(milliseconds / 1000.0)


def _stop_pwm() -> None:
    global _buzzer_pwm
    if _buzzer_pwm is not None:
        try:
            _buzzer_pwm.stop()
        except Exception:
            pass
        _buzzer_pwm = None


def cleanup() -> None:
    _stop_pwm()
    try:
        if _buzzer_pin is not None:
            GPIO.output(_buzzer_pin, GPIO.LOW)
    except Exception:
        pass
    try:
        GPIO.cleanup()
    except Exception:
        pass
