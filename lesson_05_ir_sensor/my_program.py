from helper import (
    light_off,
    light_on,
    pause_ms,
    pick_how_led_turns_on,
    pick_when_blocked_is,
    prepare_ir_sensor,
    prepare_led,
    something_nearby,
)

LED_PIN = 26
LED_ON_LEVEL = ""
IR_PIN = None
BLOCKED_IS = ""


def my_program():
    # Step 1 — LED and IR settings (flip BLOCKED_IS if the LED never reacts)
    # pick_how_led_turns_on(LED_ON_LEVEL)
    # pick_when_blocked_is(BLOCKED_IS)
    # prepare_led(LED_PIN)
    # prepare_ir_sensor(IR_PIN)
    #
    # Step 2 — poll for ~6 s: LED on when something is nearby, off when clear
    # for _ in range(120):
    #     if something_nearby():
    #         light_on()
    #     else:
    #         light_off()
    #     pause_ms(50)
    pass
