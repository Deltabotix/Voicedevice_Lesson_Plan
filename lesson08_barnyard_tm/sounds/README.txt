Put short **mono PCM WAV** files here (e.g. `meow.wav`, `woof.wav`) for **playback**
when the model wins — not for Teachable Machine training.

Training audio: record on the Pi with  python3 tm_pack_class.py CLASSNAME  ,
zip per class, upload in TM (see ~/lessons/TM_AUDIO_WORKFLOW.txt).

In `challenge.py`, point `LABEL_TO_SOUND` at these paths. Keys must match your
Teachable Machine **class names** exactly.
