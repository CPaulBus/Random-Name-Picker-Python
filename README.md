<img width="180" height="180" alt="bangboo-scanner" src="https://github.com/user-attachments/assets/9253842c-6a93-4424-a2d4-9bc73f6e1d66" />

# Bangboo Scanner
> **Automated OCR Screenshot Data Extractor & State Manager**

A Python CLI tool using computer vision (`EasyOCR`) to extract, parse, and filter structured text data directly from graphical application screenshots. It utilizes positional noise-filtering heuristics and set mathematics to maintain persistent selection pools across program restarts.

Now available both as Python source code and as a standalone Windows executable (`.exe`).

---

## ✨ Key Features

* **Automated Image OCR:** Extracts raw text from application UI screenshots using deep-learning-powered `EasyOCR`.
* **Heuristic Noise Filtering:** Uses relative-positional logic to dynamically strip away static UI labels, user profile metadata, and numerical clutter.
* **Persistent State Management:** Employs Python set operations (`issubset`, set differences) to maintain selection state across execution cycles without repeating draws.
* **Automatic Pool Resets:** Detects when all available options have been selected and resets the draw pool automatically.
* **Standalone Executable:** Packaged into a binary using `PyInstaller` so users can run it without needing Python or external dependencies pre-installed.

---

## 🛠️ Tech Stack & Requirements

* **Language:** Python 3.8+
* **Computer Vision / OCR:** `EasyOCR`, `PyTorch`
* **Packaging & Deployment:** `PyInstaller`
* **Core Logic:** Python Standard Library (`random`, `os`, Set Mathematics)
* **Version Control:** Git

---

## 📥 Option 1: Standalone Executable (Quickest)

1. Go to the **[Releases](../../releases)** section on this GitHub repository.
2. Download the latest `Bangboo-Scanner.exe` binary.
3. Run `Bangboo-Scanner.exe` directly on Windows (no Python setup required).

> 💡 **Note on Windows SmartScreen Warning:**
> Because this executable is an open-source, unsigned binary, Windows Defender / SmartScreen may display a *"Windows protected your PC / Unknown Publisher"* pop-up.
> * **To run:** Click **More info** $\rightarrow$ **Run anyway**.
> * **Alternative:** Right-click `main.exe` $\rightarrow$ **Properties** $\rightarrow$ check **Unblock** at the bottom $\rightarrow$ click **Apply**.

---

## 💻 Option 2: Run from Source

### Prerequisites
Make sure you have Python installed on your machine.

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git)
   cd YOUR_REPO_NAME

2. **Create and activate a virtual environment:**
* **Windows:**
```bash
python -m venv venv
venv\Scripts\activate

```


* **macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate

```




3. **Install dependencies:**
```bash
pip install easyocr pyinstaller

```



### Running the Script

1. Place your target UI screenshot into the project directory.
2. Run the main script:
```bash
python main.py

```



---

## ⚠️ Disclaimer

This project is an independent, non-commercial open-source tool developed strictly for personal utility and educational purposes to learn Python, computer vision, and state management. 

* **AI Assistance & Educational Purpose:** Project code structures and design assets/concepts were created with the assistance of **Google Gemini** as a pair-programming and learning tool.
* **Non-Affiliation:** This project is not affiliated, associated, authorized, endorsed by, or in any way officially connected with HoYoverse (COGNOSPHERE PTE. LTD.) or any of its subsidiaries.
* **Intellectual Property:** All product names, trademarks, screenshots, character names, and registered trademarks belong to their respective copyright owners.
* **Safety & Integrity:** This software does not interact with game memory, modify game files, or automate gameplay. It operates exclusively on standard user-provided image files.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](https://www.google.com/search?q=./LICENSE) for more information.
