"""
Lesson 2 challenge — MOSFET + 12 V LED strip + servo (Module 2).
Uses BCM pin 12 for strip brightness (PWM %). Servo must use one kit AUX pin.

Edit: SERVO_PIN, student_flow().
"""
import time
import RPi.GPIO as GPIO

# MOSFET / 12 V LED strip (this kit: BCM 12 only)
MOSFET_PIN = 12

# TODO: Servo signal pin — must be one of 4, 5, 6, 17, 27 (BCM). Pick from your wiring diagram.
SERVO_PIN = None

_mosfet_pwm = None
_servo_pwm = None
_SERVO_AUX = frozenset({4, 5, 6, 17, 27})


def student_flow():
    # Example order (see LESSON_2_GUIDE.txt):
    #
    # setup_mosfet_strip()
    # setup_servo(SERVO_PIN)
    #
    # Servo: left / middle / right (angles you choose, 0–180)
    #   set_servo_angle(0);   wait_seconds(...)
    #   set_servo_angle(90);  wait_seconds(...)
    #   set_servo_angle(180); wait_seconds(...)
    #
    # Strip: a few brightness steps or a simple ramp, then off
    #   set_strip_brightness_percent(0)
    #   ramp_strip_brightness(0, 60, step=15, pause_ms=120)   # optional “fade”
    #   set_strip_brightness_percent(0)   # must end with strip off
    pass


def run_with_guard():
    try:
        student_flow()
    except ValueError as e:
        print(f"Input error: {e}")
    except RuntimeError as e:
        print(f"Hardware error: {e}")
    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        safe_cleanup()
        print("Cleanup complete.")


def main():
    run_with_guard()


def setup_mosfet_strip() -> None:
    """PWM on MOSFET pin to dim the 12 V strip (adapter powers the strip; Pi only switches)."""
    global _mosfet_pwm
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    GPIO.setup(MOSFET_PIN, GPIO.OUT)
    _mosfet_pwm = GPIO.PWM(MOSFET_PIN, 1000)
    _mosfet_pwm.start(0.0)


def set_strip_brightness_percent(percent: float) -> None:
    """Duty 0 = strip off, 100 = full PWM on (keep within safe classroom cap in guide)."""
    global _mosfet_pwm
    if _mosfet_pwm is None:
        raise RuntimeError("Call setup_mosfet_strip() first.")
    p = max(0.0, min(100.0, float(percent)))
    _mosfet_pwm.ChangeDutyCycle(p)


def ramp_strip_brightness(
    start_percent: float,
    end_percent: float,
    step: float = 10.0,
    pause_ms: int = 100,
) -> None:
    """Step brightness from start to end for a simple visible 'fade' (still PWM steps)."""
    if step <= 0:
        raise ValueError("step must be positive.")
    a, b = float(start_percent), float(end_percent)
    if abs(a - b) < 1e-6:
        set_strip_brightness_percent(a)
        return
    if a <= b:
        levels = []
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
        set_strip_brightness_percent(level)
        wait_ms(pause_ms)


def setup_servo(pin: int) -> None:
    """50 Hz PWM for a standard hobby servo on an allowed AUX pin."""
    global _servo_pwm
    if not isinstance(pin, int):
        raise ValueError("SERVO_PIN must be an integer BCM number.")
    if pin not in _SERVO_AUX:
        raise ValueError(f"SERVO_PIN must be one of {sorted(_SERVO_AUX)} for this kit.")
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    _servo_pwm = GPIO.PWM(pin, 50)
    _servo_pwm.start(0.0)


def set_servo_angle(angle: float) -> None:
    """Move servo to angle 0–180° (typical duty 2.5% … 12.5% at 50 Hz)."""
    global _servo_pwm
    if _servo_pwm is None:
        raise RuntimeError("Call setup_servo() first.")
    ang = max(0.0, min(180.0, float(angle)))
    duty = 2.5 + (ang / 180.0) * 10.0
    _servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.45)
    _servo_pwm.ChangeDutyCycle(0.0)


def wait_seconds(seconds: float) -> None:
    if seconds < 0:
        raise ValueError("seconds cannot be negative.")
    time.sleep(seconds)


def wait_ms(milliseconds: int) -> None:
    if milliseconds < 0:
        raise ValueError("milliseconds cannot be negative.")
    time.sleep(milliseconds / 1000.0)


def _stop_mosfet_pwm() -> None:
    global _mosfet_pwm
    if _mosfet_pwm is not None:
        try:
            _mosfet_pwm.ChangeDutyCycle(0)
            _mosfet_pwm.stop()
        except Exception:
            pass
        _mosfet_pwm = None


def _stop_servo_pwm() -> None:
    global _servo_pwm
    if _servo_pwm is not None:
        try:
            _servo_pwm.ChangeDutyCycle(0)
            _servo_pwm.stop()
        except Exception:
            pass
        _servo_pwm = None


def safe_cleanup() -> None:
    _stop_mosfet_pwm()
    _stop_servo_pwm()
    try:
        GPIO.cleanup()
    except Exception:
        pass


if __name__ == "__main__":
    main()
