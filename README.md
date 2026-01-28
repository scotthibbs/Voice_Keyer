# Voice Keyer

A standalone voice keyer for amateur radio operators. Assign voice messages to F1-F8 keys using text-to-speech or your own recorded audio.

## Features

- **8 programmable F-key slots** (F1-F8) for quick message playback
- **Text-to-Speech mode** - type a message and have it spoken automatically
- **Recording mode** - record your own voice for each slot (requires `sounddevice` and `soundfile`)
- **Per-slot mode switching** - mix TTS and recorded messages across slots
- **Adjustable speed and volume** for TTS playback
- **Keyboard shortcuts** - press F1-F8 to play, Escape to stop
- **Persistent settings** - messages, modes, and voice settings saved between sessions
- **Preloaded examples** - one-click load of common amateur radio messages (CQ, signal reports, etc.)
- **Standalone executable** - build a single .exe with PyInstaller

## Requirements

- Python 3.7+
- `pyttsx3` (required)
- `sounddevice` (optional, enables recording)
- `soundfile` (optional, enables recording)
- `numpy` (optional, required with sounddevice)

The app works in TTS-only mode if `sounddevice`/`soundfile` are not installed.

## Installation

```bash
git clone https://github.com/scotthibbs/Voice_Keyer.git
cd Voice_Keyer
pip install -r requirements.txt
```

To enable recording support:

```bash
pip install sounddevice soundfile numpy
```

## Usage

```bash
python voice_keyer_tts.py
```

1. Type a message into any F-key slot and press **Play** or the corresponding F-key
2. To use a recorded message, toggle the slot to **Rec** mode, click **Record**, speak, then click **Stop**
3. Adjust TTS speed and volume with the sliders
4. Press **Escape** to stop any playback

Recordings are saved as WAV files in `~/.voice_keyer_recordings/`.
Settings are saved to `~/.voice_keyer_tts_config.json`.

## Building a Standalone Executable

```bash
python build.py
```

This produces `Voice_Keyer_TTS.exe` (Windows) using PyInstaller.

## License

MIT
