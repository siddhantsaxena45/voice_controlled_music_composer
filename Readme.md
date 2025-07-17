
# 🎙️ Voice Band Simulator 🎶

A gesture-free, voice-controlled music creation app built with Python and Pygame — record instrument loops, generate songs, and control everything using **just your voice**.

![Screenshot 1](screenshots/s%20(1).png)
![Screenshot 2](screenshots/s%20(2).png)
![Screenshot 3](screenshots/s%20(3).png)
![Screenshot 4](screenshots/s%20(4).png)
![Screenshot 5](screenshots/s%20(5).png)
![Screenshot 6](screenshots/s%20(6).png)

---

## 🧠 Features

- 🎤 Voice Command Driven (Google Speech Recognition)
- 🥁 Multiple Instruments: Piano, Guitar, Drums, Flute, Vocals
- 🎛️ Mix Loops into a Final Song
- 🎧 Real-time Playback and Looping
- 🖼️ Clean, Pygame-based GUI
- ✅ Fully Offline (after first use, FFmpeg included)

---

## 🚀 Demo Commands

### Menu Screen
```plaintext
select piano
select vocals
make song
play song
pause song
````

### Instrument Screen

```plaintext
record
play
pause
back
```

🎼 Speak notes like:

```plaintext
zero one two three four
or
0 1 2 3 4 5
```

---

## 🖥 Requirements

| Component            | Purpose                |
| -------------------- | ---------------------- |
| `pygame`             | GUI and Audio Playback |
| `pydub`              | Audio Mixing/Export    |
| `speech_recognition` | Voice Input            |
| `sounddevice`        | Audio Capture          |
| `ffmpeg`             | Required by Pydub      |

> ✅ Everything is bundled in the `.exe` distribution (no setup needed).

---

## 🔧 Run Locally (Python Setup)

### 1. Clone and Set Up Virtual Environment

```bash
git clone https://github.com/your-username/voice-band-simulator.git
cd voice-band-simulator
python -m venv venv
source venv/bin/activate    # or venv\Scripts\activate (Windows)
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt**

```txt
pygame
pydub
speechrecognition
sounddevice
```

### 3. FFmpeg Setup

Download static build of FFmpeg from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip)
Extract it and add the `bin/` folder to your system `PATH`.

---

## 🛠 Build Executable (Windows)

Install PyInstaller:

```bash
pip install pyinstaller
```

Build:

```bash
pyinstaller --onefile --add-data "assets;assets" --add-data "sounds;sounds" main.py
```

Include the following folders with the `.exe`:

* `assets/`
* `sounds/`
* `ffmpeg/bin/` with `ffmpeg.exe` inside

---

## 📁 Project Structure

```
voice-band-simulator/
├── assets/               # Images: background, instruments
├── sounds/               # Pre-recorded note samples
├── instruments/          # Auto-generated loops
├── final/                # Mixed final song
├── main.py               # Main app logic
├── README.md
├── requirements.txt
```

---

## 🙏 Special Thanks

* [Python](https://python.org)
* [PyGame](https://www.pygame.org)
* [FFmpeg](https://ffmpeg.org)
* [SpeechRecognition](https://pypi.org/project/SpeechRecognition/)
* [Gyan.dev FFmpeg Builds](https://www.gyan.dev/ffmpeg/builds/)
* 🎓 Inspired by community projects on voice-controlled audio interfaces

---

## 📜 License

MIT License
© 2025 Siddhant

---

## 🌟 Star this repo if you like it!
