"""
Train a YOLOv8 classification model on the prepared fish dataset.

Run after prepare_yolo_classify.py has created the dataset/train and dataset/val folders.

Usage:
    python train_yolo.py
"""

from ultralytics import YOLO

def main():
    # nano model = fastest, good for getting a working pipeline quickly.
    # swap to yolov8s-cls.pt or yolov8m-cls.pt later for better accuracy.
    model = YOLO("yolov8n-cls.pt")

    results = model.train(
        data="dataset",      # folder containing train/ and val/
        epochs=50,
        imgsz=224,
        batch=32,
        project="spreewald-fish",
        name="yolov8n-cls-baseline",
    )

    # quick validation summary
    metrics = model.val()
    print(metrics)

if __name__ == "__main__":
    main()
