Put one short **mono WAV** per drum voice here. File names should match the **keys**
in **BEAT_LABEL_TO_WAV** in `challenge.py` (e.g. `drum.wav`, `snare1.wav`).

If a file is missing, the lesson tries `/usr/share/sounds/alsa/*.wav` fallbacks
(see `challenge.py`).

Record or download small clips (~0.5–1.2 s). Same sample rate family as your
Teachable Machine export is not required for playback—`aplay` uses the WAV header.
