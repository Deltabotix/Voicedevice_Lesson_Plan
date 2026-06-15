import helper

LED_PIN = 26
LED_ON_LEVEL = ""

PROMPT_TEMPLATE = """
You are a strict classifier for a red LED on a Raspberry Pi.

Rules:
- If the user wants the LED turned ON or lit, reply exactly: LED_ON
- If they want it OFF or dark, reply exactly: LED_OFF
- If they are not asking to change the LED (questions, chat, other topics), reply exactly: NONE

User said: "{utterance}"

Reply with exactly one word: LED_ON, LED_OFF, or NONE
""".strip()

TEST_PHRASES = []


def my_program():
    # Step 1 — fill TEST_PHRASES and tune PROMPT_TEMPLATE above
    # helper.check_prompt_lab_ready(TEST_PHRASES, PROMPT_TEMPLATE)
    # helper.pick_how_led_turns_on(LED_ON_LEVEL)
    # helper.prepare_led(LED_PIN)
    # helper.light_off()
    #
    # Step 2 — run each test phrase through Groq and drive the LED
    # for phrase in TEST_PHRASES:
    #     label = helper.classify_led_request(phrase, PROMPT_TEMPLATE)
    #     print(f"{phrase!r} -> {label}")
    #     helper.apply_led_label(label)
    #     helper.pause(0.4)
    pass
