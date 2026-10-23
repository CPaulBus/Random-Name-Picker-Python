import warnings

from sympy.core import add

warnings.filterwarnings("ignore", category=UserWarning)

import random
import os
import easyocr
import tkinter as tk
from tkinter import filedialog, messagebox
import threading


class ZZZNamePicker:
    def __init__(self, save_filename="picked_names.txt"):
        self.save_filename = save_filename
        self.picked_names = self._load_progress()

        print("Initializing OCR Engine (this takes a moment on first run)...")
        # set gpu=True/False depending on your setup
        self.reader = easyocr.Reader(['en'], gpu=True)

        # Base UI words to ignore across all HoYoLAB screenshots
        self.base_ignore_words = [
            "uid", "lv", "recruited", "agents", "hoyolab",
            "zenless", "zone", "zero", "battle", "records",
            "proxy's", "friend", "discovering", "new", "eridu",
            "pyrois"
        ]

    def _load_progress(self):
        loaded_names = set()
        if os.path.exists(self.save_filename):
            with open(self.save_filename, "r", encoding="utf-8") as file:
                for line in file:
                    clean_name = line.strip()
                    if clean_name:
                        loaded_names.add(clean_name)
            print(f"Loaded {len(loaded_names)} previously picked agent(s) from '{self.save_filename}'.")
        return loaded_names

    def _save_single_name(self, name):
        with open(self.save_filename, "a", encoding="utf-8") as file:
            file.write(f"{name}\n")

    def _clear_saved_progress(self):
        with open(self.save_filename, "w", encoding="utf-8") as file:
            file.write("")

    def _is_valid_name(self, text, active_ignore_list):
        """Checks if text is valid using the dynamic ignore list."""
        text_lower = text.lower().strip()

        if text.isdigit() or len(text_lower) <= 1:
            return False

        for word in active_ignore_list:
            if word in text_lower:
                return False

        return True

    def extract_names_from_image(self, image_path):
        print(f"\nScanning image at: {image_path}...")
        raw_results = self.reader.readtext(image_path, detail=0)

        # Create a copy of base ignore words for this run
        active_ignore_list = list(self.base_ignore_words)

        # --- IMPROVED USERNAME DETECTION ---
        for i, text in enumerate(raw_results):
            if "uid" in text.lower():
                # Walk backwards from UID to find the actual username
                for j in range(i - 1, -1, -1):
                    candidate = raw_results[j].strip()
                    cand_lower = candidate.lower()

                    # Check if this candidate is just another UI element
                    is_ui_text = any(word in cand_lower for word in self.base_ignore_words)

                    # If it's not UI text, it MUST be the player's username!
                    if not is_ui_text and len(candidate) > 0:
                        detected_username = candidate
                        print(f"Auto-detected player username: '{detected_username}'")
                        active_ignore_list.append(detected_username.lower())
                        break
                break

        # Filter the OCR results using the updated list
        extracted_names = set()
        for text in raw_results:
            clean_str = text.strip()
            if self._is_valid_name(clean_str, active_ignore_list):
                if (clean_str == "Ye" or clean_str == "Shunguang") and ("Ye Shunguang" not in extracted_names):
                    extracted_names.add("Ye Shunguang")

                elif clean_str == "Orphie &":
                    extracted_names.add("Orphie & Magus")

                elif (clean_str == "Ju" or clean_str == "Fufu") and ("Ju Fufu" not in extracted_names):
                    extracted_names.add("Ju Fufu")

                elif (clean_str == "Zhu" or clean_str == "Yuan") and ("Zhu Yuan" not in extracted_names):
                    extracted_names.add("Zhu Yuan")

                elif (clean_str == "Astra" or clean_str == "Yao") and ("Astra Yao" not in extracted_names):
                    extracted_names.add("Astra Yao")

                elif (clean_str == "Nangong" or clean_str == "Yu") and ("Nangong Yu" not in extracted_names):
                    extracted_names.add("Nangong Yu")

                elif (clean_str == "Soldier" or clean_str == "11") and ("Soldier 11" not in extracted_names):
                    extracted_names.add("Soldier 11")

                else:
                    extracted_names.add(clean_str)

        return extracted_names

    def pick_random_name(self, image_path):
        extracted_names = self.extract_names_from_image(image_path)

        if not extracted_names:
            return None, 0, 0

        # Reset Logic
        reset_triggered = False
        if extracted_names.issubset(self.picked_names):
            print("\nAll agents in this screenshot have been picked! Clearing history and resetting pool...")
            self.picked_names.clear()
            self._clear_saved_progress()
            reset_triggered = True

        available_names = extracted_names - self.picked_names
        chosen_name = random.choice(list(available_names))

        self.picked_names.add(chosen_name)
        self._save_single_name(chosen_name)

        print(f"\nSelected Agent: {chosen_name}")
        print(f"Progress: {len(self.picked_names)} / {len(extracted_names)} agents picked from this image set.")

        return chosen_name, len(self.picked_names), len(extracted_names), reset_triggered


class ZZZGUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zenless Zone Zero Random Name Picker")
        self.root.geometry("560x450")
        self.root.minsize(500, 400)
        self.root.configure(bg="#1e1e1e")

        self.picker = None
        self.selected_image_path = tk.StringVar()

        self._build_ui()

        # Initialize backend picker in a separate thread so the window opens instantly
        threading.Thread(target=self._init_picker, daemon=True).start()

    def _init_picker(self):
        self.status_label.config(text="Status: Initializing OCR Engine...", fg="#f39c12")
        self.picker = ZZZNamePicker()
        self.status_label.config(text="Status: Ready. Load a screenshot to begin.", fg="#2ecc71")
        self.browse_btn.config(state=tk.NORMAL)

    def _build_ui(self):
        # Title Header
        title_frame = tk.Frame(self.root, bg="#1e1e1e")
        title_frame.pack(pady=15)

        title_label = tk.Label(
            title_frame, text="ZENLESS ZONE ZERO",
            font=("Arial", 16, "bold"), fg="#3498db", bg="#1e1e1e"
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame, text="Agent Name Picker & Tracker",
            font=("Arial", 10), fg="#b0b0b0", bg="#1e1e1e"
        )
        subtitle_label.pack()

        # File Selection Frame
        file_frame = tk.Frame(self.root, bg="#2a2a2a", padx=10, pady=10)
        file_frame.pack(fill=tk.X, padx=20, pady=5)

        path_entry = tk.Entry(
            file_frame, textvariable=self.selected_image_path,
            font=("Arial", 10), bg="#333333", fg="#ffffff", insertbackground="white", relief=tk.FLAT
        )
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=5)

        self.browse_btn = tk.Button(
            file_frame, text="Browse Image", font=("Arial", 9, "bold"),
            bg="#3498db", fg="#ffffff", activebackground="#2980b9", activeforeground="white",
            relief=tk.FLAT, command=self.browse_image, state=tk.DISABLED, cursor="hand2"
        )
        self.browse_btn.pack(side=tk.RIGHT, ipadx=10, ipady=3)

        # Action Button Frame
        action_frame = tk.Frame(self.root, bg="#1e1e1e")
        action_frame.pack(pady=10)

        self.pick_btn = tk.Button(
            action_frame, text="Pick Random Agent", font=("Arial", 11, "bold"),
            bg="#2ecc71", fg="#ffffff", activebackground="#27ae60", activeforeground="white",
            relief=tk.FLAT, command=self.run_picker, state=tk.DISABLED, cursor="hand2"
        )
        self.pick_btn.pack(ipadx=20, ipady=8)

        # Results Display Card
        result_card = tk.Frame(self.root, bg="#252525", bd=1, relief=tk.SOLID, padx=15, pady=15)
        result_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(result_card, text="SELECTED AGENT:", font=("Arial", 9, "bold"), fg="#888888", bg="#252525").pack(
            anchor="w")

        self.result_label = tk.Label(
            result_card, text="Waiting for input...", font=("Arial", 18, "bold"),
            fg="#f1c40f", bg="#252525", wraplength=450
        )
        self.result_label.pack(pady=(10, 5), anchor="w")

        self.progress_label = tk.Label(
            result_card, text="Progress: 0 / 0 picked", font=("Arial", 9),
            fg="#aaaaaa", bg="#252525"
        )
        self.progress_label.pack(anchor="w", pady=(5, 0))

        # Status Bar Footer
        self.status_label = tk.Label(
            self.root, text="Status: Loading OCR engine...", font=("Arial", 9, "italic"),
            fg="#f39c12", bg="#1e1e1e", anchor="w"
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=8)

    def browse_image(self):
        file_path = filedialog.askopenfilename(
            title="Select HoYoLAB Screenshot",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if file_path:
            self.selected_image_path.set(file_path)
            self.pick_btn.config(state=tk.NORMAL)

    def run_picker(self):
        image_path = self.selected_image_path.get().strip()
        if not image_path or not os.path.isfile(image_path):
            messagebox.showerror("Error", "Please select a valid image file first!")
            return

        self.status_label.config(text="Status: Scanning image and picking agent...", fg="#f39c12")
        self.pick_btn.config(state=tk.DISABLED)
        self.browse_btn.config(state=tk.DISABLED)

        # Run extraction in a background thread to prevent UI freezing
        threading.Thread(target=self._process_image_thread, args=(image_path,), daemon=True).start()

    def _process_image_thread(self, image_path):
        try:
            result = self.picker.pick_random_name(image_path)
            if not result:
                self.root.after(0, lambda: self._update_ui_error("No valid agent names found in the image."))
                return

            chosen_name, picked_count, total_count, reset_triggered = result
            self.root.after(0, lambda: self._update_ui_success(chosen_name, picked_count, total_count, reset_triggered))
        except Exception as e:
            self.root.after(0, lambda: self._update_ui_error(f"Error: {str(e)}"))

    def _update_ui_success(self, chosen_name, picked_count, total_count, reset_triggered):
        self.result_label.config(text=chosen_name)
        self.progress_label.config(text=f"Progress: {picked_count} / {total_count} agents picked from this image set.")

        status_msg = "Status: Successfully picked agent!"
        if reset_triggered:
            status_msg = "Status: All agents were picked! Pool was automatically reset."

        self.status_label.config(text=status_msg, fg="#2ecc71")
        self.pick_btn.config(state=tk.NORMAL)
        self.browse_btn.config(state=tk.NORMAL)

    def _update_ui_error(self, error_message):
        self.result_label.config(text="None")
        self.status_label.config(text=f"Status: {error_message}", fg="#e74c3c")
        self.pick_btn.config(state=tk.NORMAL)
        self.browse_btn.config(state=tk.NORMAL)
        messagebox.showwarning("Notice", error_message)


# --- Run GUI Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ZZZGUIApp(root)
    root.mainloop()