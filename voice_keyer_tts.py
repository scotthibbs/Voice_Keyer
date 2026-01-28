#!/usr/bin/env python3
"""
Voice Keyer with Text-to-Speech - Amateur Radio Voice Message Player
Uses TTS to generate voice messages with a female voice
Supports recorded voice messages via sounddevice/soundfile
"""

import tkinter as tk
from tkinter import messagebox, ttk
import pyttsx3
import json
import threading
import numpy as np
from pathlib import Path

# Optional recording support
try:
    import sounddevice as sd
    import soundfile as sf
    RECORDING_AVAILABLE = True
except ImportError:
    RECORDING_AVAILABLE = False

RECORDINGS_DIR = Path.home() / ".voice_keyer_recordings"


class VoiceKeyerTTS:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Keyer - Text-to-Speech")
        self.root.geometry("800x650")
        self.root.minsize(700, 550)

        # Find preferred voice ID on startup
        self.preferred_voice_id = self._find_female_voice_id()

        # Configuration file
        self.config_file = Path.home() / ".voice_keyer_tts_config.json"
        self.message_slots = {}
        self.slot_modes = {}  # "tts" or "rec" per slot
        self.load_config()

        # Ensure recordings directory exists
        RECORDINGS_DIR.mkdir(exist_ok=True)

        # Recording state
        self.is_recording = False
        self.recording_key = None
        self.recorded_data = []

        # Create GUI
        self.create_widgets()

        # Bind keyboard shortcuts
        self.bind_shortcuts()

        # Playing flag
        self.is_playing = False

    def _find_female_voice_id(self):
        """Find a female voice ID to use."""
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        voice_id = None
        for voice in voices:
            if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                voice_id = voice.id
                break
            elif any(name in voice.name.lower() for name in ['zira', 'hazel', 'samantha', 'victoria', 'karen']):
                voice_id = voice.id
                break
        if voice_id is None and len(voices) > 1:
            voice_id = voices[1].id
        engine.stop()
        del engine
        return voice_id

    def _create_engine(self):
        """Create a fresh TTS engine with current settings."""
        engine = pyttsx3.init()
        if self.preferred_voice_id:
            engine.setProperty('voice', self.preferred_voice_id)
        engine.setProperty('rate', self.speed_var.get())
        engine.setProperty('volume', self.volume_var.get())
        return engine

    def _recording_path(self, key):
        """Return the WAV file path for a given F-key slot."""
        return RECORDINGS_DIR / f"{key}.wav"

    def _has_recording(self, key):
        """Check if a recording exists for the given key."""
        return self._recording_path(key).exists()

    def _recording_duration(self, key):
        """Get duration in seconds of a recording, or None."""
        path = self._recording_path(key)
        if not path.exists():
            return None
        try:
            info = sf.info(str(path))
            return info.duration
        except Exception:
            return None

    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="Voice Keyer - Text-to-Speech", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # Instructions
        instructions = tk.Label(
            self.root,
            text="Enter text messages for F1-F8 keys, then press the key to speak the message",
            font=("Arial", 10)
        )
        instructions.pack(pady=5)

        # Voice settings frame
        settings_frame = tk.LabelFrame(self.root, text="Voice Settings", padx=10, pady=5)
        settings_frame.pack(pady=5, padx=20, fill=tk.X)

        # Speed control
        tk.Label(settings_frame, text="Speed:").grid(row=0, column=0, padx=5)
        self.speed_var = tk.IntVar(value=150)
        speed_scale = tk.Scale(
            settings_frame,
            from_=80,
            to=250,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            length=200
        )
        speed_scale.grid(row=0, column=1, padx=5)

        # Volume control
        tk.Label(settings_frame, text="Volume:").grid(row=0, column=2, padx=5)
        self.volume_var = tk.DoubleVar(value=1.0)
        volume_scale = tk.Scale(
            settings_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            length=200
        )
        volume_scale.grid(row=0, column=3, padx=5)

        # Frame for message slots
        self.slots_frame = tk.Frame(self.root)
        self.slots_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Create 8 slots for F1-F8
        self.text_entries = {}
        self.play_buttons = {}
        self.mode_vars = {}
        self.record_buttons = {}
        self.rec_labels = {}
        self.tts_frames = {}
        self.rec_frames = {}

        for i in range(1, 9):
            key = f"F{i}"
            frame = tk.Frame(self.slots_frame)
            frame.pack(fill=tk.X, pady=3)

            # Key label
            key_label = tk.Label(frame, text=f"{key}:", width=4, font=("Arial", 10, "bold"))
            key_label.pack(side=tk.LEFT, padx=(5, 2))

            # Mode toggle
            mode = self.slot_modes.get(key, "tts")
            mode_var = tk.StringVar(value=mode)
            self.mode_vars[key] = mode_var

            if RECORDING_AVAILABLE:
                mode_frame = tk.Frame(frame)
                mode_frame.pack(side=tk.LEFT, padx=2)
                tts_rb = tk.Radiobutton(mode_frame, text="TTS", variable=mode_var, value="tts",
                                        command=lambda k=key: self._on_mode_change(k))
                tts_rb.pack(side=tk.LEFT)
                rec_rb = tk.Radiobutton(mode_frame, text="Rec", variable=mode_var, value="rec",
                                        command=lambda k=key: self._on_mode_change(k))
                rec_rb.pack(side=tk.LEFT)

            # TTS frame (text entry)
            tts_frame = tk.Frame(frame)
            self.tts_frames[key] = tts_frame

            text_entry = tk.Entry(tts_frame, font=("Arial", 10))
            text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            text_entry.insert(0, self.message_slots.get(key, ""))
            text_entry.bind('<FocusOut>', lambda e, k=key: self.save_message(k))
            text_entry.bind('<Return>', lambda e, k=key: self.play_message(k))
            self.text_entries[key] = text_entry

            # Rec frame (recording info + record button)
            rec_frame = tk.Frame(frame)
            self.rec_frames[key] = rec_frame

            rec_label = tk.Label(rec_frame, text="No recording", font=("Arial", 9), width=20, anchor=tk.W)
            rec_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            self.rec_labels[key] = rec_label

            if RECORDING_AVAILABLE:
                rec_btn = tk.Button(
                    rec_frame, text="Record", width=8,
                    command=lambda k=key: self._toggle_recording(k),
                    bg="#888888", fg="white"
                )
                rec_btn.pack(side=tk.LEFT, padx=2)
                self.record_buttons[key] = rec_btn

            # Play button
            play_btn = tk.Button(
                frame,
                text="Play",
                command=lambda k=key: self.play_message(k),
                bg="#4CAF50",
                fg="white",
                width=8
            )
            play_btn.pack(side=tk.RIGHT, padx=5)
            self.play_buttons[key] = play_btn

            # Show correct frame based on mode
            self._show_mode_frame(key, mode)

        # Update recording labels
        self._update_all_rec_labels()

        # Control buttons
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        stop_btn = tk.Button(
            control_frame,
            text="Stop",
            command=self.stop_speech,
            bg="#f44336",
            fg="white",
            width=15
        )
        stop_btn.pack(side=tk.LEFT, padx=5)

        test_btn = tk.Button(
            control_frame,
            text="Test Voice",
            command=self.test_voice,
            bg="#2196F3",
            fg="white",
            width=15
        )
        test_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tk.Button(
            control_frame,
            text="Clear All",
            command=self.clear_all,
            width=15
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        examples_btn = tk.Button(
            control_frame,
            text="Load Examples",
            command=self.load_examples,
            width=15
        )
        examples_btn.pack(side=tk.LEFT, padx=5)

        if not RECORDING_AVAILABLE:
            note = tk.Label(self.root,
                            text="(Install sounddevice + soundfile for recording support)",
                            font=("Arial", 8), fg="gray")
            note.pack(pady=2)

    def _show_mode_frame(self, key, mode):
        """Show the correct sub-frame (TTS or Rec) for a slot."""
        if mode == "tts":
            self.rec_frames[key].pack_forget()
            self.tts_frames[key].pack(side=tk.LEFT, fill=tk.X, expand=True)
        else:
            self.tts_frames[key].pack_forget()
            self.rec_frames[key].pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _on_mode_change(self, key):
        """Handle mode toggle for a slot."""
        mode = self.mode_vars[key].get()
        self.slot_modes[key] = mode
        self._show_mode_frame(key, mode)
        self._update_rec_label(key)
        self.save_config()

    def _update_rec_label(self, key):
        """Update the recording info label for a slot."""
        if key not in self.rec_labels:
            return
        if self._has_recording(key):
            dur = self._recording_duration(key)
            if dur is not None:
                self.rec_labels[key].config(text=f"Recorded ({dur:.1f}s)")
            else:
                self.rec_labels[key].config(text="Recorded")
        else:
            self.rec_labels[key].config(text="No recording")

    def _update_all_rec_labels(self):
        for i in range(1, 9):
            self._update_rec_label(f"F{i}")

    def _toggle_recording(self, key):
        """Start or stop recording for a slot."""
        if not RECORDING_AVAILABLE:
            return

        if self.is_recording:
            if self.recording_key == key:
                self._stop_recording()
            return

        # Start recording
        self.is_recording = True
        self.recording_key = key
        self.recorded_data = []
        self.record_buttons[key].config(text="Stop", bg="#f44336")
        self.rec_labels[key].config(text="Recording...")

        samplerate = 44100

        def callback(indata, frames, time_info, status):
            self.recorded_data.append(indata.copy())

        self._rec_stream = sd.InputStream(samplerate=samplerate, channels=1, callback=callback)
        self._rec_stream.start()

    def _stop_recording(self):
        """Stop the current recording and save to file."""
        if not self.is_recording:
            return

        key = self.recording_key
        self._rec_stream.stop()
        self._rec_stream.close()

        if self.recorded_data:
            data = np.concatenate(self.recorded_data, axis=0)
            path = self._recording_path(key)
            sf.write(str(path), data, 44100)

        self.is_recording = False
        self.recording_key = None
        self.recorded_data = []

        self.record_buttons[key].config(text="Record", bg="#888888")
        self._update_rec_label(key)

    def bind_shortcuts(self):
        """Bind F1-F8 keys to speak messages"""
        for i in range(1, 9):
            self.root.bind(f"<F{i}>", lambda e, k=f"F{i}": self.play_message(k))

        # ESC to stop
        self.root.bind("<Escape>", lambda e: self.stop_speech())

    def save_message(self, key):
        """Save message text from entry field"""
        text = self.text_entries[key].get().strip()
        if text:
            self.message_slots[key] = text
        elif key in self.message_slots:
            del self.message_slots[key]
        self.save_config()

    def play_message(self, key):
        """Play the message assigned to key (TTS or recording)."""
        mode = self.mode_vars[key].get() if key in self.mode_vars else "tts"

        if mode == "rec" and RECORDING_AVAILABLE:
            self._play_recording(key)
        else:
            self._play_tts(key)

    def _play_tts(self, key):
        """Speak the TTS message for a key."""
        self.save_message(key)
        text = self.text_entries[key].get().strip()

        if not text:
            messagebox.showwarning("No Message", f"No message entered for {key}")
            return

        if self.is_playing:
            return

        self.play_buttons[key].config(bg="#FFA500", text="Playing")

        def speak():
            try:
                self.is_playing = True
                engine = self._create_engine()
                engine.say(text)
                engine.runAndWait()
                engine.stop()
                del engine
            except Exception as e:
                print(f"Error speaking: {e}")
            finally:
                self.is_playing = False
                self.root.after(0, lambda: self.play_buttons[key].config(bg="#4CAF50", text="Play"))

        thread = threading.Thread(target=speak, daemon=True)
        thread.start()

    def _play_recording(self, key):
        """Play a recorded WAV file for a key."""
        path = self._recording_path(key)
        if not path.exists():
            messagebox.showwarning("No Recording", f"No recording saved for {key}")
            return

        if self.is_playing:
            return

        self.play_buttons[key].config(bg="#FFA500", text="Playing")

        def play():
            try:
                self.is_playing = True
                data, samplerate = sf.read(str(path))
                sd.play(data, samplerate)
                sd.wait()
            except Exception as e:
                print(f"Error playing recording: {e}")
            finally:
                self.is_playing = False
                self.root.after(0, lambda: self.play_buttons[key].config(bg="#4CAF50", text="Play"))

        thread = threading.Thread(target=play, daemon=True)
        thread.start()

    def stop_speech(self):
        """Stop currently playing speech - resets flag so next play works"""
        self.is_playing = False
        if RECORDING_AVAILABLE:
            try:
                sd.stop()
            except Exception:
                pass
        if self.is_recording:
            self._stop_recording()
        for btn in self.play_buttons.values():
            btn.config(bg="#4CAF50", text="Play")

    def test_voice(self):
        """Test the current voice settings"""
        if self.is_playing:
            return

        test_text = "CQ CQ CQ, this is Whiskey One Alpha Bravo Charlie, calling CQ and standing by."

        def speak():
            try:
                self.is_playing = True
                engine = self._create_engine()
                engine.say(test_text)
                engine.runAndWait()
                engine.stop()
                del engine
            except Exception as e:
                print(f"Error in test: {e}")
            finally:
                self.is_playing = False

        thread = threading.Thread(target=speak, daemon=True)
        thread.start()

    def load_examples(self):
        """Load example messages for amateur radio"""
        examples = {
            "F1": "CQ CQ CQ, this is Whiskey One Alpha Bravo Charlie, calling CQ and standing by.",
            "F2": "You are five nine, five nine. My QTH is Chicago Illinois.",
            "F3": "Roger, copied. Thanks for the contact. 73 and good DX.",
            "F4": "This is Whiskey One Alpha Bravo Charlie.",
            "F5": "Please repeat your call sign. Say again please.",
            "F6": "Thank you for the QSO. 73 and best wishes.",
            "F7": "Contest number five nine nine, zone zero four.",
            "F8": "Signal report is five by nine. You are loud and clear."
        }

        if messagebox.askyesno("Load Examples",
                               "This will replace all current messages with examples. Continue?"):
            for key, text in examples.items():
                self.text_entries[key].delete(0, tk.END)
                self.text_entries[key].insert(0, text)
                self.message_slots[key] = text
                if key in self.mode_vars:
                    self.mode_vars[key].set("tts")
                    self.slot_modes[key] = "tts"
                    self._show_mode_frame(key, "tts")
            self.save_config()

    def clear_all(self):
        """Clear all messages"""
        if messagebox.askyesno("Clear All", "Remove all message assignments?"):
            self.message_slots.clear()
            for entry in self.text_entries.values():
                entry.delete(0, tk.END)
            self.save_config()

    def save_config(self):
        """Save configuration to file"""
        try:
            # Build per-slot config with mode info
            messages = {}
            for i in range(1, 9):
                key = f"F{i}"
                mode = self.slot_modes.get(key, "tts")
                text = self.message_slots.get(key, "")
                messages[key] = {"mode": mode, "text": text}

            config = {
                'messages': messages,
                'speed': self.speed_var.get(),
                'volume': self.volume_var.get()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    raw_messages = config.get('messages', {})
                    # Support both old format (string) and new format (dict with mode/text)
                    for key, val in raw_messages.items():
                        if isinstance(val, dict):
                            self.message_slots[key] = val.get("text", "")
                            self.slot_modes[key] = val.get("mode", "tts")
                        else:
                            # Old format: plain string
                            self.message_slots[key] = val
                            self.slot_modes[key] = "tts"
                    if 'speed' in config:
                        self.speed_var = tk.IntVar(value=config['speed'])
                    if 'volume' in config:
                        self.volume_var = tk.DoubleVar(value=config['volume'])
        except Exception as e:
            print(f"Error loading config: {e}")
            self.message_slots = {}


def main():
    root = tk.Tk()
    app = VoiceKeyerTTS(root)
    root.mainloop()

if __name__ == "__main__":
    main()
