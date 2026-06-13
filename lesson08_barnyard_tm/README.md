# Lesson 8: Barnyard soundboard (Teachable Machine — Module 8)

## Goal

Train an **audio** model in [Teachable Machine](https://teachablemachine.withgoogle.com/) (e.g. cat, dog, sheep, cow + **background**). Export **TensorFlow Lite**, copy **`model.tflite`** (or `soundclassifier_with_metadata.tflite`) and **`labels.txt`** from the zip into this folder, map each class name to a **WAV**, and run. The lesson uses **`tflite_runtime`** + **`sounddevice`** + **`numpy`** (small install compared to MediaPipe).

## Files

| File | Purpose |
|------|---------|
| **LESSON_8_GUIDE.txt** | Theory, fill-in list, every helper |
| **challenge.py** | `LABEL_TO_SOUND`, thresholds, `SAMPLE_RATE`, `student_flow()` |
| **starter.py** | Runs `challenge.py` |
| **requirements.txt** | `tflite-runtime`, `numpy`, `sounddevice` |
| **sounds/** | Put your WAV files here (see `sounds/README.txt`) |

## What to copy from the Teachable Machine zip

1. **TensorFlow Lite** model — either name is accepted (first found wins):
   - `model.tflite` (rename the export if you like), or  
   - `soundclassifier_with_metadata.tflite`
2. **`labels.txt`** — class names in **output index order** (one label per line; lines like `0 Background Noise` are OK).

See **Getting files onto the Pi** in `LESSON_8_GUIDE.txt` for USB and browser paths.

### Copy from your PC to the Pi with `scp`

Run on **your laptop or desktop** (where the exported files are), not on the Pi. Replace `USER`, `PI_IP`, and the path if your home or lesson directory differs.

```bash
# Model + labels into the lesson folder
scp model.tflite labels.txt USER@PI_IP:~/Voicedevice/lessons/lesson08_barnyard_tm/

# If you did not rename the model:
scp soundclassifier_with_metadata.tflite labels.txt USER@PI_IP:~/Voicedevice/lessons/lesson08_barnyard_tm/

# Optional: copy a directory of WAVs
scp -r sounds USER@PI_IP:~/Voicedevice/lessons/lesson08_barnyard_tm/
```

Examples: `voicedevice@192.168.1.42:~/Voicedevice/lessons/lesson08_barnyard_tm/` or `voicedevice@raspberrypi.local:~/Voicedevice/lessons/lesson08_barnyard_tm/`. The Pi must have **SSH** enabled; the first time you may be prompted to accept the host key.

## Requirements

- Raspberry Pi with **mic** and **speaker** working (Lessons 4–5 help).
- **Waveform model**: input must be **float32** audio with a fixed window (e.g. shape `[1, 44032]` at **16 kHz**). This matches common TM TFLite exports used with `Interpreter` + raw samples. **4D spectrogram** inputs are not supported here (clear error at load).
- **Python**: `python3 -m pip install -r requirements.txt`  
  - **`tflite-runtime`**: same family as the kit wake-word path; much smaller than full TensorFlow or MediaPipe.  
  - **`sounddevice`**: needs **PortAudio**; on Raspberry Pi OS often: `sudo apt install portaudio19-dev` then `pip install sounddevice`.
- **System**: `aplay` (alsa-utils).

## What you change in `challenge.py`

1. **`LABEL_TO_SOUND`** — keys match **`labels.txt`** (same names as in Teachable Machine); values are **`Path`** or **string** paths to WAV files.  
2. **`IGNORE_LABELS`** — background class names that must not trigger sounds.  
3. **`SAMPLE_RATE`** — must match your model (often **16000**).  
4. **INMP441 / room noise** — `REMOVE_DC_OFFSET`, `AMBIENT_CALIB_SEC`, `AMBIENT_GATE_MULT`, `AMBIENT_DYNAMIC_MIN_SCORE` in `challenge.py` (stay quiet during calibration).  
5. **`MIN_SCORE`**, **`COOLDOWN_SEC`**, **`LOOP_SLEEP_SEC`**, **`OUTPUT_DEVICE`**, **`MIC_DEVICE`** as needed.

## Run

```bash
cd ~/Voicedevice/lessons/lesson08_barnyard_tm
python3 -m pip install -r requirements.txt
python3 challenge.py
```

## Success

Speaking a trained class prints something like `→ cat (0.82) play meow.wav` and you hear the file. Background noise should mostly stay silent when **`MIN_SCORE`** and **`IGNORE_LABELS`** match your training.

## Troubleshooting: pip / disk

If **`No space left on device`**, free space on **`/`** and **`/tmp`** (`df -h`), then e.g. `sudo apt clean`, `pip cache purge`, and retry with `python3 -m pip install --no-cache-dir -r requirements.txt`. This stack is **much smaller** than MediaPipe but still needs enough room for wheels and unpack.

## Troubleshooting: sounddevice

If `import sounddevice` fails after pip install, install PortAudio dev headers and reinstall:

```bash
sudo apt install portaudio19-dev
python3 -m pip install --force-reinstall sounddevice
```

Use `python3 -m sounddevice` to list input devices; set **`MIC_DEVICE`** in `challenge.py` to an **integer index** if the default mic is wrong.
