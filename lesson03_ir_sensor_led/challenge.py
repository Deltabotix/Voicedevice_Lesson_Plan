"""
Lesson 3 challenge — IR sensor + red LED (Module 3).
Poll the IR pin; when an obstacle is detected, turn the LED on (or blink — see guide).

Edit: IR_PIN, ON_STATE_KEYWORD, IR_OBSTACLE_KEYWORD, student_flow().
"""
import time
import RPi.GPIO as GPIO

# Red LED (this kit: BCM 26)
LED_PIN = 26

# TODO: GPIO level for LED “on”: "HIGH" or "LOW"
ON_STATE_KEYWORD = ""

ON_STATE = None

# TODO: BCM pin where the IR sensor output connects (see kit diagram; often an AUX pin)
IR_PIN = None

# TODO: What does the IR pin read when something is in front? "HIGH" or "LOW" (flip if backwards)
IR_OBSTACLE_KEYWORD = ""

IR_OBSTACLE_IS_HIGH = None


def student_flow():
    # Suggested flow (see LESSON_3_GUIDE.txt):
    #
    # set_on_state(ON_STATE_KEYWORD)
    # setup_led(LED_PIN)
    # set_ir_obstacle_level(IR_OBSTACLE_KEYWORD)
    # setup_ir_sensor(IR_PIN)
    #
    # Poll loop (example: ~6 s at 50 ms per step → 120 iterations):
    #   for _ in range(120):
    #       if obstacle_present():
    #           led_on()
    #       else:
    #           led_off()
    #       wait_ms(50)
    #
    # Or blink while obstacle: if obstacle_present(): led_on(); wait_ms(...); led_off(); ...
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
    if not isinstance(pin, int):
        raise ValueError("LED pin must be an integer BCM number.")
    if ON_STATE is None:
        raise RuntimeError("Call set_on_state() before setup_led().")
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)


def led_on() -> None:
    if ON_STATE is None:
        raise RuntimeError("Call set_on_state() first.")
    GPIO.output(LED_PIN, ON_STATE)


def led_off() -> None:
    if ON_STATE is None:
        raise RuntimeError("Call set_on_state() first.")
    off = GPIO.LOW if ON_STATE == GPIO.HIGH else GPIO.HIGH
    GPIO.output(LED_PIN, off)


def set_ir_obstacle_level(keyword: str) -> None:
    """Obstacle = pin reads HIGH, or obstacle = pin reads LOW — depends on your IR module."""
    global IR_OBSTACLE_IS_HIGH
    k = (keyword or "").strip().upper()
    if k == "HIGH":
        IR_OBSTACLE_IS_HIGH = True
        return
    if k == "LOW":
        IR_OBSTACLE_IS_HIGH = False
        return
    raise ValueError('IR_OBSTACLE_KEYWORD must be "HIGH" or "LOW".')


def setup_ir_sensor(pin: int) -> None:
    if not isinstance(pin, int):
        raise ValueError("IR_PIN must be an integer BCM number.")
    if IR_OBSTACLE_IS_HIGH is None:
        raise RuntimeError("Call set_ir_obstacle_level() before setup_ir_sensor().")
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    # Many breakout boards work with internal pull-up; if readings float, try PUD_DOWN in a fork lesson.
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def obstacle_present() -> bool:
    if IR_PIN is None:
        raise RuntimeError("Set IR_PIN before reading.")
    v = GPIO.input(IR_PIN)
    if IR_OBSTACLE_IS_HIGH:
        return v == GPIO.HIGH
    return v == GPIO.LOW


def wait_ms(milliseconds: int) -> None:
    if milliseconds < 0:
        raise ValueError("Milliseconds cannot be negative.")
    time.sleep(milliseconds / 1000.0)


def safe_cleanup() -> None:
    try:
        led_off()
    except Exception:
        pass
    try:
        GPIO.cleanup()
    except Exception:
        pass


if __name__ == "__main__":
    main()
