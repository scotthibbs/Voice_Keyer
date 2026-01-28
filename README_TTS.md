# Voice Keyer with Text-to-Speech

A Python 3 voice keyer program for amateur radio operators that uses text-to-speech with a female voice to speak your messages.

## Features

- **8 Message Slots**: Assign text messages to F1-F8 function keys
- **Female Voice**: Automatically selects a female TTS voice
- **Quick Playback**: Press F1-F8 to instantly speak your message
- **Adjustable Settings**: Control speech speed and volume
- **GUI Interface**: Easy-to-use graphical interface
- **Configuration Persistence**: Messages and settings saved between sessions
- **Example Messages**: Pre-loaded amateur radio messages
- **Emergency Stop**: Press ESC to stop speech immediately

## Installation

1. Make sure you have Python 3 installed (3.7 or higher recommended)

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install pyttsx3 directly:
```bash
pip install pyttsx3
```

### Platform-Specific Requirements

**Windows:**
- No additional requirements, uses built-in SAPI5

**macOS:**
- Uses built-in NSSpeechSynthesizer
- No additional requirements

**Linux:**
```bash
# Install espeak
sudo apt-get install espeak

# Or install festival
sudo apt-get install festival
```

## Usage

1. Run the program:
```bash
python3 voice_keyer_tts.py
```

2. **Set up your messages:**
   - Type text messages in the entry fields for F1-F8
   - Messages are automatically saved when you click away
   - Press Enter in a text field to test that message

3. **Adjust voice settings:**
   - Use the Speed slider to adjust speaking rate (80-250 WPM)
   - Use the Volume slider to adjust loudness (0.0-1.0)

4. **During operation:**
   - Press F1-F8 to speak the corresponding message
   - Press ESC to stop playback
   - Click "▶ Play" buttons to test individual messages
   - Click "🔊 Test Voice" to hear a sample transmission

5. **Quick start:**
   - Click "Load Examples" to populate all slots with amateur radio examples
   - Modify the examples to match your callsign and preferences

## Example Messages

The program includes example messages for common amateur radio operations:

- **F1**: CQ call - "CQ CQ CQ, this is [callsign], calling CQ and standing by"
- **F2**: Signal report and location
- **F3**: Acknowledgment and sign-off
- **F4**: Station identification
- **F5**: Repeat request
- **F6**: Thank you message
- **F7**: Contest exchange
- **F8**: Signal report

## Tips for Best Results

### Message Composition
- Use phonetic alphabet for callsigns (Whiskey One Alpha)
- Spell out numbers clearly
- Keep messages concise (5-20 seconds)
- Use proper radio terminology
- Add pauses with commas or periods

### Voice Customization
- Slower speeds (100-130) sound more natural
- Faster speeds (180-220) work for contests
- Test different speeds to find what sounds best
- Volume can be adjusted to match your rig

### Common Messages to Program

**General Operating:**
- CQ call with your callsign
- Signal report response
- QTH (location) information
- Station identification
- "Thanks and 73" sign-off

**Contest Operation:**
- CQ contest call
- Exchange sending
- Quick acknowledgment
- Station ID
- Repeat request

**DX Operation:**
- CQ DX call
- Pileup instructions
- Signal reports
- QSL information

## Phonetic Alphabet Reference

The TTS engine will speak these clearly:

- A = Alpha, B = Bravo, C = Charlie, D = Delta
- E = Echo, F = Foxtrot, G = Golf, H = Hotel
- I = India, J = Juliet, K = Kilo, L = Lima
- M = Mike, N = November, O = Oscar, P = Papa
- Q = Quebec, R = Romeo, S = Sierra, T = Tango
- U = Uniform, V = Victor, W = Whiskey, X = X-ray
- Y = Yankee, Z = Zulu

## Keyboard Shortcuts

- **F1-F8**: Speak corresponding message
- **ESC**: Stop current speech
- **Enter** (in text field): Test that message

## Configuration

Settings are automatically saved to `~/.voice_keyer_tts_config.json`

The configuration file stores:
- All message texts
- Speech speed setting
- Volume setting

## Troubleshooting

**No voice or silent:**
- Check volume slider is not at 0
- Verify system audio is working
- On Linux, ensure espeak or festival is installed

**Wrong voice (male instead of female):**
- The program tries to auto-select a female voice
- Available voices depend on your operating system
- Windows usually has Zira (female) available
- macOS has Samantha, Victoria, or Karen
- Linux voices vary by TTS engine installed

**Speech sounds robotic:**
- Try adjusting the speed slider
- Lower speeds (100-130) often sound more natural
- Some TTS engines sound better than others

**Function keys not working:**
- Make sure the program window has focus
- Some systems may capture F-keys for other functions

## Advanced Customization

### Manual Voice Selection

If you want to change voices manually, you can modify the code to list available voices:

```python
import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    print(f"ID: {voice.id}")
    print(f"Name: {voice.name}")
    print(f"Languages: {voice.languages}")
    print("---")
```

### Adding More Slots

You can easily modify the code to add more function keys (F9-F12) by changing the loop range from `range(1, 9)` to `range(1, 13)`.

## Requirements

- Python 3.7+
- pyttsx3 2.90+
- tkinter (usually included with Python)
- Platform-specific TTS engine (see Installation)

## Advantages Over Pre-Recorded Audio

- **Flexibility**: Change messages anytime without re-recording
- **Consistency**: Same quality every time
- **No Equipment Needed**: No microphone or audio recording required
- **Easy Updates**: Just type new text to update messages
- **Space Efficient**: No large audio files to store

## License

Free to use and modify for amateur radio operations.

## Contributing

Feel free to suggest improvements or report issues!

73 de Voice Keyer
