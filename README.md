# Zenless Zone Zero — OCR Random Agent Picker

An automated Python-based random character picker for **Zenless Zone Zero (ZZZ)**. Instead of manually entering character names, simply drag and drop a screenshot of your agent roster (e.g., from HoYoLAB Battle Records), and the tool uses Optical Character Recognition (OCR) to parse, filter, and randomly pick an agent for you.

---

## ✨ Features

* **📸 Image Text Extraction:** Powered by `easyocr` to read character names directly from game screenshots.
* **🧠 Smart Noise & Username Filtering:**
* Automatically filters out UI clutter (e.g., *"Lv. 60"*, *"UID"*, *"Battle Records"*).
* Auto-detects the player's username near the header and ignores it so it's never mistaken for an agent.


* **💾 Persistent Drawing Pool:** Remembers picked agents in a local `picked_names.txt` file so progress carries over between sessions.
* **🔄 Automatic Pool Reset:** Automatically clears history and resets the pool once every extracted agent from the screenshot has been drawn.
* **🖱️ Fast CLI Workflow:** Works with simple drag-and-drop file paths right in your terminal.

---

## 🛠️ Prerequisites & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/zzz-random-picker.git
cd zzz-random-picker

```

### 2. Install Required Packages

Run the following command in your terminal or PyCharm terminal:

```bash
pip install easyocr opencv-python

```

> **Note on PyTorch / GPU:** By default, `easyocr` will run on your CPU. If you have an NVIDIA GPU and want faster processing, install PyTorch with CUDA support:
> ```bash
> pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
> 
> ```
> 
> 

---

## 🚀 How to Use

1. **Take a Screenshot:** Capture your ZZZ agent roster or grab your character grid from HoYoLAB Battle Records.
2. **Run the Script:**
```bash
python main.py

```


3. **Drag & Drop:** When prompted in the terminal, drag your image file directly into the terminal window and press `Enter`.
4. **Get Your Pick:** The program will scan the image, filter out UI elements, pick a random agent, and save the choice to `picked_names.txt`.

---

## 📂 Project Structure

```text
├── main.py              # Main application logic and CLI loop
├── picked_names.txt     # Generated save file tracking drawn agents
├── README.md            # Project documentation
└── .gitignore           # Git ignore settings

```

---

## ⚙️ How It Works Under the Hood

1. **OCR Scan:** `EasyOCR` scans the image and outputs raw text strings.
2. **Dynamic Blacklisting:** The script searches for UI keywords and walks backward from `"UID"` to isolate and ignore the player's username dynamically.
3. **Set Difference Engine:** Computes `Extracted Agents - Picked Agents` using Python `set` operations to build the remaining pool.
4. **Reset Validation:** If `Extracted Agents` is a subset of `Picked Agents` (`issubset()`), the script clears `picked_names.txt` and resets the draw state automatically.

---

---

## 💡 Project Intent & Disclaimer

* **Educational & Portfolio Use:** This repository was created as a hands-on project to upskill in Python programming, Optical Character Recognition (OCR) implementation, state management, and Git workflows.
* **AI Collaboration:** Built with pair-programming support from **Google Gemini** for architectural planning, code optimization, and documentation.
* **Non-Commercial Notice:** This project is strictly for personal, non-commercial, and educational purposes. 
* **Intellectual Property:** *Zenless Zone Zero*, character names, and assets are trademarks and copyright of **HoYoverse (COGNOSPHERE PTE. LTD.)**. This tool is an unofficial fan-made utility and is not affiliated with or endorsed by HoYoverse.

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---