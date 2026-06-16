import time

import RPi.GPIO as GPIO

_ALLOWED_SERVO_PINS = frozenset({4, 5, 6, 17, 27})
_servo_pin: int | None = None
_servo_pwm = None


def prepare_servo(pin: int) -> None:
    global _servo_pin, _servo_pwm
    if not isinstance(pin, int):
        raise ValueError("SERVO_PIN must be a whole number (BCM pin).")
    if pin not in _ALLOWED_SERVO_PINS:
        raise ValueError(f"SERVO_PIN must be one of {sorted(_ALLOWED_SERVO_PINS)} for this kit.")
    GPIO.setwarnings(False)
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    _servo_pin = pin
    _servo_pwm = GPIO.PWM(pin, 50)
    _servo_pwm.start(0.0)
    print(f"Servo ready on pin {pin}")


def move_to(angle: float) -> None:
    if _servo_pwm is None:
        raise RuntimeError("Call prepare_servo() first.")
    ang = max(0.0, min(180.0, float(angle)))
    duty = 2.5 + (ang / 180.0) * 10.0
    _servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.45)
    _servo_pwm.ChangeDutyCycle(0.0)
    print(f"Servo at {ang:.0f}°")


def pause(seconds: int) -> None:
    if seconds < 0:
        raise ValueError("Pause time cannot be negative.")
    time.sleep(seconds)


def _stop_servo_pwm() -> None:
    global _servo_pwm
    if _servo_pwm is not None:
        try:
            _servo_pwm.ChangeDutyCycle(0)
            _servo_pwm.stop()
        except Exception:
            pass
        _servo_pwm = None


def cleanup() -> None:
    if _servo_pin is None:
        return
    _stop_servo_pwm()
    try:
        GPIO.cleanup()
    except Exception:
        pass
