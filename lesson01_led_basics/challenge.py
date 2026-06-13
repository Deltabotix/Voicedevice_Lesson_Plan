"""
Lesson 1 challenge — Lights and buzzer (Module 1).
Passive buzzer: sound comes from PWM (a tone at a frequency), not a steady HIGH/LOW.

Edit: LED_PIN, ON_STATE_KEYWORD, BUZZER_PIN, BUZZER_FREQ_HZ (optional), student_flow().
"""
import time
import RPi.GPIO as GPIO

# --- LED (red) ---
# TODO 1: BCM pin for the red LED (this kit: 26)
LED_PIN = None

# TODO 2: GPIO level that means LED on: "HIGH" or "LOW"
ON_STATE_KEYWORD = ""

ON_STATE = None

# --- Passive buzzer (PWM tone) ---
# TODO 3: BCM pin for the buzzer (see kit diagram; example 22)
BUZZER_PIN = None

# TODO 4 (optional): tone pitch in Hz — piezo passives often like ~2000–4000 (default 2500)
BUZZER_FREQ_HZ = 2500

# Internal: PWM object while a tone is playing
_buzzer_pwm = None


def student_flow():
    # Student zone — build this flow (see LESSON_1_GUIDE.txt):
    #
    # LED part:
    #   set_on_state(ON_STATE_KEYWORD)
    #   setup_led(LED_PIN)
    #   led_on()
    #   wait_seconds(3)
    #   led_off()
    #
    # Passive buzzer (short — short — long):
    #   setup_buzzer(BUZZER_PIN)
    #   passive_tone(duration_ms, BUZZER_FREQ_HZ)   # short beep
    #   wait_ms(gap between beeps)
    #   passive_tone(duration_ms, BUZZER_FREQ_HZ)   # short beep
    #   wait_ms(gap)
    #   passive_tone(longer_ms, BUZZER_FREQ_HZ)     # long beep
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


# ----- LED helpers -----

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
        raise ValueError("LED pin must be an integer BCM pin number.")
    if ON_STATE is None:
        raise RuntimeError("Call set_on_state() before setup_led().")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)


def led_on() -> None:
    if ON_STATE is None:
        raise RuntimeError("ON_STATE is not set. Call set_on_state() first.")
    GPIO.output(LED_PIN, ON_STATE)
    print("LED is ON")


def led_off() -> None:
    if ON_STATE is None:
        raise RuntimeError("ON_STATE is not set. Call set_on_state() first.")
    off_state = GPIO.LOW if ON_STATE == GPIO.HIGH else GPIO.HIGH
    GPIO.output(LED_PIN, off_state)
    print("LED is OFF")


def wait_seconds(seconds: int) -> None:
    if seconds < 0:
        raise ValueError("Wait time cannot be negative.")
    time.sleep(seconds)


# ----- Passive buzzer (PWM) -----

def _stop_buzzer_pwm() -> None:
    global _buzzer_pwm
    if _buzzer_pwm is not None:
        try:
            _buzzer_pwm.stop()
        except Exception:
            pass
        _buzzer_pwm = None


def setup_buzzer(pin: int) -> None:
    if not isinstance(pin, int):
        raise ValueError("Buzzer pin must be an integer BCM pin number.")
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)


def passive_tone(duration_ms: int, frequency_hz: int = 2500) -> None:
    """
    Play a tone on the passive buzzer for duration_ms using software PWM.
    frequency_hz is how fast the pin toggles — higher often sounds sharper.
    """
    global _buzzer_pwm
    if BUZZER_PIN is None:
        raise RuntimeError("Set BUZZER_PIN before calling passive_tone.")
    if duration_ms < 0:
        raise ValueError("duration_ms cannot be negative.")
    if frequency_hz < 50 or frequency_hz > 8000:
        raise ValueError("frequency_hz: use a value in a sensible range (e.g. 2000–4000).")

    _stop_buzzer_pwm()
    _buzzer_pwm = GPIO.PWM(BUZZER_PIN, frequency_hz)
    _buzzer_pwm.start(50)
    time.sleep(duration_ms / 1000.0)
    _stop_buzzer_pwm()


def wait_ms(milliseconds: int) -> None:
    if milliseconds < 0:
        raise ValueError("Milliseconds cannot be negative.")
    time.sleep(milliseconds / 1000.0)


def safe_cleanup() -> None:
    _stop_buzzer_pwm()
    try:
        GPIO.cleanup()
    except Exception:
        pass


if __name__ == "__main__":
    main()