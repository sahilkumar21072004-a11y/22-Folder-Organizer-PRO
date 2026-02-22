import os
import shutil
import json
import logging
from datetime import datetime

# =============================
# Logging Setup
# =============================

logging.basicConfig(
    filename="organizer_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

UNDO_FILE = "undo_move.json"

# =============================
# File Categories
# =============================

FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi"],
    "Music": [".mp3", ".wav"],
    "Archives": [".zip", ".rar", ".7z"],
    "Scripts": [".py", ".js", ".html", ".css"]
}

# =============================
# Helper Functions
# =============================

def save_undo(data):
    with open(UNDO_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_undo():
    if not os.path.exists(UNDO_FILE):
        return None
    with open(UNDO_FILE, "r") as f:
        return json.load(f)


def detect_downloads():
    return os.path.join(os.path.expanduser("~"), "Downloads")


def get_category(extension):
    for folder, extensions in FILE_TYPES.items():
        if extension.lower() in extensions:
            return folder
    return "Others"


def organize_folder(folder_path, dry_run=False):
    if not os.path.exists(folder_path):
        print("❌ Folder does not exist.")
        return

    undo_data = {}

    files = [
        f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]

    print(f"\n📂 Found {len(files)} files.\n")

    for file in files:
        old_path = os.path.join(folder_path, file)
        _, ext = os.path.splitext(file)

        category = get_category(ext)
        dest_folder = os.path.join(folder_path, category)

        if not os.path.exists(dest_folder):
            if not dry_run:
                os.makedirs(dest_folder)

        new_path = os.path.join(dest_folder, file)

        # Conflict-safe move
        counter = 1
        while os.path.exists(new_path):
            name, extension = os.path.splitext(file)
            new_filename = f"{name}_{counter}{extension}"
            new_path = os.path.join(dest_folder, new_filename)
            counter += 1

        if dry_run:
            print(f"🔍 Preview: {file} → {category}/")
        else:
            shutil.move(old_path, new_path)
            undo_data[new_path] = old_path
            logging.info(f"Moved: {file} → {category}")
            print(f"✅ Moved: {file} → {category}")

    if not dry_run:
        save_undo(undo_data)
        print("\n💾 Undo data saved.")

    print("\n🎉 Organization Completed.\n")


def undo_last(folder_path):
    data = load_undo()
    if not data:
        print("⚠ No undo data found.")
        return

    for new_path, old_path in data.items():
        if os.path.exists(new_path):
            shutil.move(new_path, old_path)
            print(f"↩ Restored: {os.path.basename(new_path)}")

    print("✅ Undo completed.")
    logging.info("Undo operation performed.")


# =============================
# CLI Interface
# =============================

if __name__ == "__main__":

    print("===== Folder Organizer PRO =====")
    print("1. Organize Folder")
    print("2. Undo Last Organization")

    choice = input("Choose option (1/2): ").strip()

    folder = input("Enter folder path (leave blank for Downloads): ").strip()

    if not folder:
        folder = detect_downloads()

    if choice == "2":
        undo_last(folder)
    else:
        dry = input("Dry run? (yes/no): ").strip().lower() == "yes"
        organize_folder(folder, dry_run=dry)