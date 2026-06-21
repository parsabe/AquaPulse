"""
Converts Fish_Data (final_all_index.txt + images/cropped) into a YOLOv8
classification-ready folder structure:

    dataset/
      train/
        species_a/
          img1.jpg
        species_b/
          ...
      val/
        species_a/
        species_b/

Usage:
    python prepare_yolo_classify.py
"""

import os
import random
import shutil
from pathlib import Path

# ---------------- CONFIG ----------------
INDEX_FILE = r"Fish_Data\final_all_index.txt"
CROPPED_DIR = r"Fish_Data\images\cropped"
OUTPUT_DIR = r"dataset"                      # where to build train/val folders
VAL_SPLIT = 0.2                               # 20% of each class goes to val
MIN_IMAGES_PER_CLASS = 3                      # skip species with too few images
SEED = 42
# -----------------------------------------

random.seed(SEED)

def find_image_file(cropped_dir, filename_stem):
    """Find the actual image file (any extension) matching filename_stem."""
    for ext in (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"):
        candidate = Path(cropped_dir) / f"{filename_stem}{ext}"
        if candidate.exists():
            return candidate
    return None

def main():
    # 1. Parse index file: class_id=species=image_type=filename=row_number
    species_to_files = {}
    missing = 0
    total = 0

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("=")
            if len(parts) != 5:
                continue
            _, species, _, filename, _ = parts
            total += 1

            img_path = find_image_file(CROPPED_DIR, filename)
            if img_path is None:
                missing += 1
                continue

            species_to_files.setdefault(species, []).append(img_path)

    print(f"Parsed {total} index entries.")
    print(f"Found {total - missing} matching image files, {missing} missing.")
    print(f"Total species: {len(species_to_files)}")

    # 2. Filter out species with too few images
    species_to_files = {
        sp: files for sp, files in species_to_files.items()
        if len(files) >= MIN_IMAGES_PER_CLASS
    }
    print(f"Species kept after min-image filter ({MIN_IMAGES_PER_CLASS}+): {len(species_to_files)}")

    # 3. Build train/val folder structure
    out = Path(OUTPUT_DIR)
    if out.exists():
        shutil.rmtree(out)

    train_count, val_count = 0, 0

    for species, files in species_to_files.items():
        random.shuffle(files)
        n_val = max(1, int(len(files) * VAL_SPLIT))
        val_files = files[:n_val]
        train_files = files[n_val:]

        train_dir = out / "train" / species
        val_dir = out / "val" / species
        train_dir.mkdir(parents=True, exist_ok=True)
        val_dir.mkdir(parents=True, exist_ok=True)

        for f in train_files:
            shutil.copy2(f, train_dir / f.name)
            train_count += 1
        for f in val_files:
            shutil.copy2(f, val_dir / f.name)
            val_count += 1

    print(f"\nDone. Train images: {train_count}, Val images: {val_count}")
    print(f"Dataset ready at: {out.resolve()}")

if __name__ == "__main__":
    main()
