import helper

LED_PIN = 26
LED_ON_LEVEL = ""
BLINK_ON_CONTROL = True

PROMPT_TEMPLATE = """
You are a traffic cop for a voice-controlled Raspberry Pi kit.

Decide whether the user sentence is asking to CONTROL physical hardware on the device
(motors, LEDs, lights, buzzer, servo, strip brightness, sensors as commands, "turn on…"),
or is GENERAL conversation (questions, facts, chat, math) that should NOT route to hardware.

Reply with exactly one word:
- CONTROL — hardware command or request to actuate something.
- GENERAL — normal talk, questions, or anything that is not a direct hardware command.

User said: "{utterance}"

Reply with exactly one word: CONTROL or GENERAL
""".strip()

TEST_PHRASES = []


def my_program():
    # Step 1 — fill TEST_PHRASES; tune PROMPT_TEMPLATE if tags are wrong
    # helper.check_traffic_lab_ready(TEST_PHRASES, PROMPT_TEMPLATE)
    # helper.pick_how_led_turns_on(LED_ON_LEVEL)
    # helper.prepare_led(LED_PIN)
    # helper.light_off()
    #
    # Step 2 — classify each phrase; blink LED on CONTROL
    # for phrase in TEST_PHRASES:
    #     tag = helper.classify_route(phrase, PROMPT_TEMPLATE)
    #     print(f"{phrase!r} -> {tag}")
    #     helper.blink_on_control(tag, BLINK_ON_CONTROL)
    #     helper.pause(0.35)
    pass
