import ctypes
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
import torchvision

import random
import os
import easyocr
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from PIL import Image, ImageTk, ImageSequence
from tkinterdnd2 import DND_FILES, TkinterDnD


class AnimatedGifLabel(tk.Label):
    """A custom Tkinter Label that handles playing animated GIFs seamlessly without borders."""

    def __init__(self, master, gif_path, size=(55, 55), *args, **kwargs):
        kwargs.setdefault('bd', 0)
        kwargs.setdefault('highlightthickness', 0)
        kwargs.setdefault('relief', tk.FLAT)

        super().__init__(master, *args, **kwargs)
        self.gif_path = gif_path
        self.size = size
        self.frames = []
        self.delay = 100  # Default fallback delay in milliseconds
        self._load_gif()

        if self.frames:
            self.current_frame = 0
            self.config(image=self.frames[0])
            self.animate()

    def _load_gif(self):
        if not os.path.exists(self.gif_path):
            return
        try:
            pil_gif = Image.open(self.gif_path)
            self.delay = pil_gif.info.get('duration', 100)
            if self.delay < 20:
                self.delay = 100

            for frame in ImageSequence.Iterator(pil_gif):
                resized_frame = frame.resize(self.size, Image.Resampling.LANCZOS)
                self.frames.append(ImageTk.PhotoImage(resized_frame))
        except Exception as e:
            print(f"Error loading GIF: {e}")

    def animate(self):
        if self.frames:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.config(image=self.frames[self.current_frame])
            self.after(self.delay, self.animate)


class ZZZNamePicker:
    def __init__(self, save_filename="picked_names.txt", on_username_detected=None):
        self.save_filename = save_filename
        self.picked_names = self._load_progress()
        self.on_username_detected = on_username_detected

        print("Initializing OCR Engine (this takes a moment on first run)...")
        self.reader = easyocr.Reader(['en'], gpu=True)

        # Base UI words to ignore across all HoYoLAB screenshots
        self.base_ignore_words = [
            "uid", "lv", "recruited", "agents", "hoyolab",
            "zenless", "zone", "zero", "battle", "records",
            "proxy's", "friend", "discovering", "new", "eridu",
            "pyrois", "Yuan"
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
        raw_results = self.reader.readtext(image_path, detail=1)

        active_ignore_list = list(self.base_ignore_words)

        # --- USERNAME DETECTION ---
        for i, (bbox, text, prob) in enumerate(raw_results):
            if "uid" in text.lower():
                for j in range(i - 1, -1, -1):
                    cand_bbox, candidate, cand_prob = raw_results[j]
                    candidate = candidate.strip()
                    cand_lower = candidate.lower()
                    is_ui_text = any(word in cand_lower for word in self.base_ignore_words)
                    if not is_ui_text and len(candidate) > 0:
                        detected_username = candidate
                        print(f"Auto-detected player username: '{detected_username}'")
                        active_ignore_list.append(detected_username.lower())

                        if self.on_username_detected:
                            self.on_username_detected(detected_username)
                        break
                break

        # Filter individual valid tokens
        valid_tokens = []
        for bbox, text, prob in raw_results:
            clean_str = text.strip()
            if self._is_valid_name(clean_str, active_ignore_list):
                p0, p1, p2, p3 = bbox
                x_center = (p0[0] + p1[0]) / 2
                y_min = min(p0[1], p1[1])
                y_max = max(p2[1], p3[1])
                valid_tokens.append({
                    'bbox': bbox,
                    'text': clean_str,
                    'x_center': x_center,
                    'y_min': y_min,
                    'y_max': y_max
                })

        valid_tokens.sort(key=lambda t: t['y_min'])

        # --- INTELLIGENT VERTICAL NAME MERGER ---
        merged_names_data = []
        skip_indices = set()

        for i in range(len(valid_tokens)):
            if i in skip_indices:
                continue
            curr = valid_tokens[i]
            curr_text = curr['text']
            curr_bbox = curr['bbox']

            for j in range(i + 1, len(valid_tokens)):
                if j in skip_indices:
                    continue
                nxt = valid_tokens[j]

                # Match words in the same vertical column stack (e.g., Zhu + Yuan, Ye + Shunguang)
                if abs(curr['x_center'] - nxt['x_center']) < 30:
                    vertical_gap = nxt['y_min'] - curr['y_max']
                    if -5 < vertical_gap < 35:
                        curr_text = f"{curr_text} {nxt['text']}"
                        curr_bbox = [
                            curr_bbox[0],
                            curr_bbox[1],
                            nxt['bbox'][2],
                            nxt['bbox'][3]
                        ]
                        curr['y_max'] = nxt['y_max']
                        skip_indices.add(j)
                        break

            merged_names_data.append((curr_bbox, curr_text))

        # Create folder to store cropped character icons temporarily
        os.makedirs("extracted_icons", exist_ok=True)
        pil_img = Image.open(image_path)

        extracted_names_map = {}

        for bbox, final_name in merged_names_data:
            if final_name in ("Shunguang", "Yuan"):
                continue
            if final_name == "Ye":
                final_name = "Ye Shunguang"
            elif final_name == "Zhu":
                final_name = "Zhu Yuan"
            elif final_name == "Orphie &":
                final_name = "Orphie & Magus"

            p0, p1, p2, p3 = bbox
            text_center_x = (min(p0[0], p3[0]) + max(p1[0], p2[0])) / 2
            text_top_y = min(p0[1], p1[1])
            left_edge_x = min(p0[0], p3[0])

            # --- SEPARATE CUSTOM CONDITIONS USING ELIF ---
            if final_name == "Ye Shunguang":
                box_x1 = max(0, int(left_edge_x + 10))
                box_x2 = min(pil_img.width, int(box_x1 + 105))
            elif final_name == "Zhu Yuan":
                box_x1 = max(0, int(left_edge_x - 4))
                box_x2 = min(pil_img.width, int(box_x1 + 95))
            else:
                card_half_width = 55
                box_x1 = max(0, int(text_center_x - card_half_width))
                box_x2 = min(pil_img.width, int(text_center_x + card_half_width))

            box_y2 = int(text_top_y - 6)
            box_y1 = max(0, int(box_y2 - 145))

            try:
                cropped_icon = pil_img.crop((box_x1, box_y1, box_x2, box_y2))
                icon_path = os.path.join("extracted_icons", f"{final_name}.png")
                cropped_icon.save(icon_path)
                extracted_names_map[final_name] = icon_path
            except Exception as e:
                print(f"Failed to crop icon for {final_name}: {e}")
                extracted_names_map[final_name] = None

        return extracted_names_map

    def pick_random_name(self, image_path):
        extracted_names_map = self.extract_names_from_image(image_path)

        if not extracted_names_map:
            return None, None, 0, 0, False

        extracted_names = set(extracted_names_map.keys())

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

        chosen_image_path = extracted_names_map.get(chosen_name)

        print(f"\nSelected Agent: {chosen_name}")
        print(f"Progress: {len(self.picked_names)} / {len(extracted_names)} agents picked from this image set.")

        return chosen_name, chosen_image_path, len(self.picked_names), len(extracted_names), reset_triggered


class ZZZGUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zenless Zone Zero Random Name Picker")

        width = 600
        height = 535

        # Center the window on the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(520, 450)
        self.root.configure(bg="#1e1e1e")
        self.root.overrideredirect(True)

        # --- FIX FOR ALT-TAB & TASKBAR VISIBILITY ---
        try:
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            style = style & ~0x00000080 | 0x00040000
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
            self.root.withdraw()
            self.root.deiconify()
        except Exception as e:
            print(f"Taskbar fix note: {e}")

        # Enable Drag-and-Drop support on the main window
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_file_drop)

        self.picker = None
        self.selected_image_path = tk.StringVar()
        self.photo_img = None

        self._build_ui()

        # Initialize backend picker in a separate thread so the window opens instantly
        threading.Thread(target=self._init_picker, daemon=True).start()

    def _init_picker(self):
        self.status_label.config(text="Status: Initializing OCR Engine...", fg="#f39c12")
        self.picker = ZZZNamePicker(
            on_username_detected=lambda uname: self.root.after(0, lambda: self.username_var.set(f"Detected Username: {uname}"))
        )
        self.status_label.config(text="Status: Ready. Load a screenshot to begin.", fg="#2ecc71")
        self.browse_btn.config(state=tk.NORMAL)

    def _start_move(self, event):
        self.x = event.x
        self.y = event.y

    def _do_move(self, event):
        x = event.x_root - self.x
        y = event.y_root - self.y
        self.root.geometry(f"+{x}+{y}")

    def handle_file_drop(self, event):
        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        file_path = file_path.strip('"\'')

        if os.path.isfile(file_path):
            valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.webp')
            if file_path.lower().endswith(valid_extensions):
                self.selected_image_path.set(file_path)
                self.pick_btn.config(state=tk.NORMAL)
                self.status_label.config(text="Status: Image loaded via drag-and-drop!", fg="#3498db")
            else:
                messagebox.showwarning("Invalid File", "Please drop a valid image file (PNG, JPG, etc.)!")
        else:
            messagebox.showerror("Error", "The dropped item is not a valid file.")

    def _build_ui(self):
        # Custom Title Bar / Header Frame
        title_bar = tk.Frame(self.root, bg="#1e1e1e", cursor="fleur")
        title_bar.pack(fill=tk.X, padx=10, pady=(5, 0))
        title_bar.bind("<Button-1>", self._start_move)
        title_bar.bind("<B1-Motion>", self._do_move)

        close_btn = tk.Button(
            title_bar, text="✕", font=("Arial", 10, "bold"),
            bg="#1e1e1e", fg="#aaaaaa", activebackground="#e74c3c", activeforeground="white",
            bd=0, highlightthickness=0, relief=tk.FLAT, command=self.root.destroy, cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT, anchor="n", padx=2, pady=2)

        title_content_frame = tk.Frame(self.root, bg="#1e1e1e")
        title_content_frame.pack(pady=(0, 10))
        title_content_frame.bind("<Button-1>", self._start_move)
        title_content_frame.bind("<B1-Motion>", self._do_move)

        logo_path = "animatedlogo.gif"
        if os.path.exists(logo_path):
            self.logo_widget = AnimatedGifLabel(title_content_frame, logo_path, size=(55, 55), bg="#1e1e1e")
            self.logo_widget.pack(side=tk.TOP, pady=(0, 5))
            self.logo_widget.bind("<Button-1>", self._start_move)
            self.logo_widget.bind("<B1-Motion>", self._do_move)

        title_label = tk.Label(
            title_content_frame, text="BANGBOO SCANNER",
            font=("Arial", 16, "bold"), fg="#3498db", bg="#1e1e1e"
        )
        title_label.pack()
        title_label.bind("<Button-1>", self._start_move)
        title_label.bind("<B1-Motion>", self._do_move)

        # Subtitle
        subtitle_lbl = tk.Label(
            self.root, text="Agent Name Picker & Tracker",
            font=("Segoe UI", 10), bg="#1e1e1e", fg="#aaaaaa"
        )
        subtitle_lbl.pack(pady=(0, 5))
        subtitle_lbl.bind("<Button-1>", self._start_move)
        subtitle_lbl.bind("<B1-Motion>", self._do_move)

        # Detected Username Label
        self.username_var = tk.StringVar(value="Detected Username: None")
        username_lbl = tk.Label(
            self.root, textvariable=self.username_var,
            font=("Segoe UI", 9, "italic"), bg="#1e1e1e", fg="#4da6ff"
        )
        username_lbl.pack(pady=(0, 10))
        username_lbl.bind("<Button-1>", self._start_move)
        username_lbl.bind("<B1-Motion>", self._do_move)

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

        # Results Display Card with Image & Text
        result_card = tk.Frame(self.root, bg="#252525", bd=1, relief=tk.SOLID, padx=15, pady=15)
        result_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.image_label = tk.Label(result_card, bg="#252525", width=100, height=120)
        self.image_label.pack(side=tk.LEFT, padx=(0, 15))

        info_frame = tk.Frame(result_card, bg="#252525")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(info_frame, text="SELECTED AGENT:", font=("Arial", 9, "bold"), fg="#888888", bg="#252525").pack(anchor="w")

        self.result_label = tk.Label(
            info_frame, text="Waiting for input...", font=("Arial", 16, "bold"),
            fg="#f1c40f", bg="#252525", wraplength=300
        )
        self.result_label.pack(pady=(5, 5), anchor="w")

        self.progress_label = tk.Label(
            info_frame, text="Progress: 0 / 0 picked", font=("Arial", 9),
            fg="#aaaaaa", bg="#252525"
        )
        self.progress_label.pack(anchor="w", pady=(5, 0))

        # Status Bar Footer
        self.status_label = tk.Label(
            self.root, text="Status: Loading OCR engine...", font=("Arial", 9, "italic"),
            fg="#f39c12", bg="#1e1e1e", anchor="w"
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=8)

        # Loading Progress Bar
        self.progress_bar = ttk.Progressbar(
            self.root, orient="horizontal", mode="indeterminate", length=540
        )
        self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 5))

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

        self.progress_bar.start(10)
        threading.Thread(target=self._process_image_thread, args=(image_path,), daemon=True).start()

    def _process_image_thread(self, image_path):
        try:
            result = self.picker.pick_random_name(image_path)
            if not result or result[0] is None:
                self.root.after(0, lambda: self._update_ui_error("No valid agent names found in the image."))
                return

            chosen_name, chosen_image_path, picked_count, total_count, reset_triggered = result
            self.root.after(
                0, lambda: self._update_ui_success(chosen_name, chosen_image_path, picked_count, total_count, reset_triggered)
            )
        except Exception as e:
            err_msg = str(e)
            self.root.after(0, lambda: self._update_ui_error(f"Error: {err_msg}"))

    def _update_ui_success(self, chosen_name, chosen_image_path, picked_count, total_count, reset_triggered):
        self.progress_bar.stop()
        self.result_label.config(text=chosen_name)
        self.progress_label.config(text=f"Progress: {picked_count} / {total_count} agents picked from this image set.")

        if chosen_image_path and os.path.exists(chosen_image_path):
            img = Image.open(chosen_image_path)
            img = img.resize((100, 120), Image.Resampling.LANCZOS)
            self.photo_img = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.photo_img, text="")
        else:
            self.image_label.config(image="", text="No Image")

        status_msg = "Status: Successfully picked agent!"
        if reset_triggered:
            status_msg = "Status: All agents were picked! Pool was automatically reset."

        self.status_label.config(text=status_msg, fg="#2ecc71")
        self.pick_btn.config(state=tk.NORMAL)
        self.browse_btn.config(state=tk.NORMAL)

    def _update_ui_error(self, error_message):
        self.progress_bar.stop()
        self.result_label.config(text="None")
        self.image_label.config(image="", text="")
        self.status_label.config(text=f"Status: {error_message}", fg="#e74c3c")
        self.pick_btn.config(state=tk.NORMAL)
        self.browse_btn.config(state=tk.NORMAL)
        messagebox.showwarning("Notice", error_message)


# --- Run GUI Application using TkinterDnD ---
if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ZZZGUIApp(root)
    root.mainloop()