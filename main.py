import warnings

warnings.filterwarnings("ignore", category=UserWarning)

import random
import os
import easyocr


class ZZZNamePicker:
    def __init__(self, save_filename="picked_names.txt"):
        self.save_filename = save_filename
        self.picked_names = self._load_progress()

        print("Initializing OCR Engine (this takes a moment on first run)...")
        # set gpu=False to run smoothly on CPU without hardware warnings
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
                extracted_names.add(clean_str)

        return extracted_names

    def pick_random_name(self, image_path):
        extracted_names = self.extract_names_from_image(image_path)

        if not extracted_names:
            print("No valid agent names found in the image.")
            return None

        # Reset Logic
        if extracted_names.issubset(self.picked_names):
            print("\nAll agents in this screenshot have been picked! Clearing history and resetting pool...")
            self.picked_names.clear()
            self._clear_saved_progress()

        available_names = extracted_names - self.picked_names
        chosen_name = random.choice(list(available_names))

        self.picked_names.add(chosen_name)
        self._save_single_name(chosen_name)

        print(f"\nSelected Agent: {chosen_name}")
        print(f"Progress: {len(self.picked_names)} / {len(extracted_names)} agents picked from this image set.")

        return chosen_name


# --- CLI Loop ---
if __name__ == "__main__":
    picker = ZZZNamePicker()

    print("\n" + "=" * 50)
    print("      ZENLESS ZONE ZERO RANDOM NAME PICKER      ")
    print("=" * 50)

    while True:
        user_input = input("\nDrag & drop your screenshot into this window (or type 'q' to quit): ").strip()

        if user_input.lower() in ['q', 'quit', 'exit']:
            print("Exiting. Goodbye!")
            break

        clean_path = user_input.strip('"\'')

        if not clean_path:
            continue

        if os.path.isfile(clean_path):
            picker.pick_random_name(clean_path)
        else:
            print("File not found. Please make sure the path is correct and try again.")
