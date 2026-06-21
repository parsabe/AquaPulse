import cv2
import numpy as np
import os
from ultralytics import YOLO
import matplotlib.pyplot as plt

# ==========================================
# 1. MSRCR PRE-PROCESSING ENGINE
# ==========================================
def apply_msrcr(img):
    img_float = np.float64(img) + 1.0
    sigmas = [15, 80, 250]
    retinex = np.zeros_like(img_float)
    for s in sigmas:
        blur = cv2.GaussianBlur(img_float, (0, 0), s)
        retinex += np.log10(img_float) - np.log10(blur)
    retinex /= len(sigmas)
    color_rest = np.log10(125.0 * img_float) - np.log10(np.sum(img_float, axis=2, keepdims=True) + 1.0)
    msrcr = retinex * color_rest
    msrcr = cv2.normalize(msrcr, None, 0, 255, cv2.NORM_MINMAX)
    return msrcr.astype(np.uint8)

# ==========================================
# 2. PIPELINE CONFIGURATION
# ==========================================


INPUT_FOLDER = Path(r"C:\Users\parsa\Desktop\Code\Screenshots")
OUTPUT_FOLDER = video_directory_path / 'image-dehazed'

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load YOLOv8 (pretrained on COCO, will fine-tune later)
model = YOLO('yolov8n.pt')

# Get list of images
image_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# ==========================================
# 3. ROBUST INFERENCE LOOP
# ==========================================
print(f"[INFO] Starting pipeline on {len(image_files)} images...")

for file_name in image_files:
    img_path = os.path.join(INPUT_FOLDER, file_name)
    img = cv2.imread(img_path)

    # Step A: Deterministic Enhancement
    enhanced_img = apply_msrcr(img)

    # Step B: Robust Detection
    # Passing the enhanced image directly to YOLO
    results = model.predict(source=enhanced_img, conf=0.25, verbose=False)

    # Step C: Visualization & Save
    result_img = results[0].plot() # YOLO native plotter
    save_path = os.path.join(OUTPUT_FOLDER, f"det_{file_name}")
    cv2.imwrite(save_path, result_img)

    print(f"[SUCCESS] Processed: {file_name}")

print("[INFO] Pipeline Complete. Detections saved to Drive.")