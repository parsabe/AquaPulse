import os
import shutil
from pathlib import Path

BASE_DIR = Path(r"C:\Users\parsa\Desktop\Code\Yolo\YOLO_Ready_Dataset")

OUTPUT_DIR = BASE_DIR.parent / "images"

def create_full_yolo_dataset():
    splits = ["train", "val", "test"]
    
    
    train_dir = BASE_DIR / "train"
    if not train_dir.exists():
        print("Error: Train directory not found!")
        return
        
    classes = sorted([d.name for d in train_dir.iterdir() if d.is_dir()])
    print(f"Found {len(classes)} classes.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    yaml_content = f"""train: ../images/train
val: ../images/val
test: ../images/test

nc: {len(classes)}
names: {classes}
"""
    with open(OUTPUT_DIR / "data.yaml", "w") as f:
        f.write(yaml_content)

    total_images = 0

    for split in splits:
        split_dir = BASE_DIR / split
        if not split_dir.exists():
            continue
            
        print(f"\nProcessing '{split}' folder...")
        
        images_out_dir = OUTPUT_DIR / "images" / split
        labels_out_dir = OUTPUT_DIR / "labels" / split
        images_out_dir.mkdir(parents=True, exist_ok=True)
        labels_out_dir.mkdir(parents=True, exist_ok=True)

        for class_id, class_name in enumerate(classes):
            class_folder = split_dir / class_name
            if not class_folder.exists():
                continue
                
            for img_path in class_folder.glob("*.*"):
                if img_path.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
                    continue
                    
                new_img_name = f"{class_name}_{img_path.name}"
                new_img_path = images_out_dir / new_img_name
                shutil.copy(img_path, new_img_path)

                label_content = f"{class_id} 0.5 0.5 0.9 0.9"
                
                label_path = labels_out_dir / f"{new_img_path.stem}.txt"
                with open(label_path, "w") as f:
                    f.write(label_content)
                    
                total_images += 1

    print(f"\n Done")
    print(f"Files are ready at: {OUTPUT_DIR}")

if __name__ == "__main__":
    create_full_yolo_dataset()