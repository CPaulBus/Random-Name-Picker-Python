<img width="180" height="180" alt="bangboo-scanner" src="https://github.com/user-attachments/assets/9253842c-6a93-4424-a2d4-9bc73f6e1d66" />

# Bangboo Scanner
> **Automated OCR Roster Scanner, Portrait Card Extractor & State Tracker**

A modern desktop application built for **Zenless Zone Zero** players. It scans HoYoLAB roster screenshots using deep-learning computer vision (`EasyOCR`), automatically extracts your player profile nickname, isolates and crops agent portrait cards, and picks a random unpicked agent with state persistence across program restarts.

Now available both as Python source code and as a standalone Windows executable (`.exe`).

---

## ✨ Key Features

- **🖼️ Deep-Learning OCR Parsing:** Extracts agent names directly from HoYoLAB roster screenshots using `EasyOCR` (GPU-accelerated).
- **👤 Auto-Detected Username:** Scans for UID proximity markers to automatically extract your in-game nickname and update the UI in real time.
- **📂 Drag-and-Drop File Ingestion:** Powered by `tkinterdnd2`—simply drop screenshots directly anywhere onto the window.
- **🧠 Vertical Name Merging:** Intelligent positional stack-matching algorithms properly group two-word agent names (e.g., *Zhu Yuan*, *Ye Shunguang*, *Orphie & Magus*) while filtering UI fragments.
- **🖼️ Character Portrait Card Cropping:** Automatically crops and isolates character icons into an `extracted_icons/` directory and renders a live preview card on the UI.
- **💾 Persistent State Management:** Saves picked agents to `picked_names.txt` to prevent duplicate picks. Automatically resets the selection pool when all agents in a screenshot set have been drawn.
- **⏳ Visual Scan Indicator:** Features a responsive progress bar and status footer to track active background scanning threads without freezing the GUI.
- **🎨 Custom Dark-Mode UI:** Features a borderless window with smooth dragging, animated GIF header (`animatedlogo.gif`), custom application icon (`BangbooScannerIcon.ico`), and native Windows taskbar/Alt-Tab integration via `ctypes`.

---

## 🛠️ Tech Stack & Requirements

- **Language:** Python 3.8+
- **GUI Framework:** Tkinter & TkinterDnD (`tkinterdnd2`)
- **Computer Vision / OCR:** `EasyOCR`, `PyTorch`
- **Image Processing:** Pillow (PIL)
- **Packaging & OS Integration:** `PyInstaller`, `ctypes`

---

## 📥 Option 1: Standalone Executable (Quickest)

1. Go to the **[Releases](../../releases)** section on this GitHub repository.
2. Download the latest `Bangboo-Scanner.zip` release bundle.
3. Extract the folder and ensure `animatedlogo.gif` and `BangbooScannerIcon.ico` remain in the directory.
4. Run `Bangboo-Scanner.exe` directly on Windows (no Python setup required).

> 💡 **Note on Windows SmartScreen Warning:**
> Because this executable is an open-source, unsigned binary, Windows Defender / SmartScreen may display a *"Windows protected your PC / Unknown Publisher"* pop-up.
> * **To run:** Click **More info** $\rightarrow$ **Run anyway**.
> * **Alternative:** Right-click `Bangboo-Scanner.exe` $\rightarrow$ **Properties** $\rightarrow$ check **Unblock** at the bottom $\rightarrow$ click **Apply**.

---

## 💻 Option 2: Run from Source

### Prerequisites
Make sure you have Python installed on your machine.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CPaulBus/Random-Name-Picker-Python.git
   cd Random-Name-Picker-Python
   ```

2. **Create and activate a virtual environment:**
   - **Windows:**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install easyocr pillow tkinterdnd2 torch torchvision pyinstaller
   ```

### Running the Application

1. Ensure `animatedlogo.gif` and `BangbooScannerIcon.ico` are present in the root directory.
2. Run the main script:
   ```bash
   python main.py
   ```

---

## 🛠️ Building the Executable from Source

To package the desktop app into a standalone `.exe` using `PyInstaller` with all static assets and dynamic C++ dependencies (`torchvision`) bundled:

```bash
pyinstaller --noconfirm --onedir --windowed --add-data "animatedlogo.gif;." --collect-all torchvision --icon="BangbooScannerIcon.ico" main.py
```

---

## ⚠️ Disclaimer

This project is an independent, non-commercial open-source tool developed strictly for personal utility and educational purposes to learn Python, computer vision, and state management. 

- **AI Assistance & Educational Purpose:** Project code structures and design assets/concepts were created with the assistance of **Google Gemini** as a pair-programming and learning tool.
- **Non-Affiliation:** This project is not affiliated, associated, authorized, endorsed by, or in any way officially connected with HoYoverse (COGNOSPHERE PTE. LTD.) or any of its subsidiaries.
- **Intellectual Property:** All product names, trademarks, screenshots, character names, and registered trademarks belong to their respective copyright owners.
- **Safety & Integrity:** This software does not interact with game memory, modify game files, or automate gameplay. It operates exclusively on standard user-provided image files.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](./LICENSE) for more information.