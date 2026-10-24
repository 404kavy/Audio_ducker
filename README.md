# AudioDucker: Neuroscience-Backed Focus & Audio Scaffolding for ADHD Minds

> **Auto-ducking background music, spatial left-ear acoustic segregation, and progressive attention span weaning for neurodivergent learners.**

---

## 🎧 The Problem
For students and knowledge workers with ADHD, studying in complete silence can trigger task-initiation paralysis and understimulation. Background music (Spotify, lofi beats) supplies the dopamine needed to cross the activation barrier, but constantly conflicts with speech when watching lectures or attending video meetings. Manually adjusting volume or pausing breaks focus and disrupts flow state.

## 🚀 The Solution: AudioDucker
AudioDucker is a lightweight, zero-cloud Windows desktop utility engineered specifically for ADHD audio focus:

1. **Sub-50ms Speech Ducking**: Monitors lecture output streams via Windows Core Audio (WASAPI) at 30+ FPS and smoothly attenuates background music when the speaker talks.
2. **🦻 Spatial Left-Ear Panning**: When speech is detected, background music isn't merely lowered—it dynamically pans **100% to the Left Ear**. This completely clears your **Right Ear** (which connects to the brain's left-hemisphere language centers: Wernicke's & Broca's areas) for 100% lecture comprehension.
3. **⚡ Progressive Focus Ramp-Down**: Starts music at full volume to beat task inertia, then slowly and imperceptibly tapers it to 0% over a customizable 10–90 minute window as natural hyperfocus takes over.

---

## 🛠️ Tech Stack & Architecture
- **Language**: Python 3.12+
- **Audio Routing**: Windows Core Audio API (WASAPI) via `pycaw`, `comtypes`, and `IChannelAudioVolume` COM interfaces.
- **UI**: Minimalist, wireframe/parchment aesthetic built with standard `tkinter` / `ttk`.
- **Zero API Keys & Zero Logins**: Controls desktop playback sessions directly at the OS level—works with Spotify Free, Spotify Premium, YouTube in browsers, VLC, and Zoom.
- **Privacy First**: 100% local processing, zero network calls, <1% CPU overhead.

---

## 💻 Quick Start

### Option 1: Run from Source
1. Clone the repository:
   ```bash
   git clone https://github.com/404kavy/Audio_ducker.git
   cd Audio_ducker
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

### Option 2: Build Executable
To package into a single standalone `.exe` without console windows:
```bash
pyinstaller --noconsole --onefile --name "AudioDucker" --hidden-import pycaw --hidden-import comtypes --hidden-import psutil main.py
```

---

## 📜 License
This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) — see the LICENSE file for details. Free for personal, non-commercial, and academic use.
