# Spreewald Fish Species Classification — YOLOv8

A YOLOv8-based image classifier for identifying fish species in the Spreewald dataset.

## Approach

Our dataset is one fish per image (no bounding boxes), so this uses **YOLOv8 classification**
(`yolov8n-cls`), not detection. It matches our data as-is, with no extra annotation work needed.

## Current baseline results

- 483 species, ~4,400 cropped images total
- Trained 50 epochs on CPU (yolov8n-cls, imgsz=224)
- **Top-1 accuracy: 30.5%** | **Top-5 accuracy: 54.6%**

Given ~8 images per species on average, this is a reasonable starting baseline (random guess
would be ~0.2%). Accuracy is mainly limited by low images-per-class, not the pipeline itself.

## Project structure

```
prepare_yolo_classify.py   # converts raw dataset + index file into YOLO classification folders
train_yolo.py               # trains the YOLOv8 classifier
.gitignore                  # excludes dataset/, runs/, model weights (too large for git)
```

## Setup

```bash
pip install ultralytics
```

## Data expected

This expects the Fish_Data dataset with:
```
Fish_Data/
  final_all_index.txt        # format: class_id=species=image_type=filename=row_number
  images/
    cropped/                 # one cropped image per fish, filenames matching the index
```

## How to run

### 1. Prepare the dataset

Edit the `CONFIG` section at the top of `prepare_yolo_classify.py` to point at your local
copy of `Fish_Data` (paths are not included in this repo since the dataset itself isn't
checked in):

```python
INDEX_FILE = r"Fish_Data\final_all_index.txt"
CROPPED_DIR = r"Fish_Data\images\cropped"
OUTPUT_DIR = r"dataset"
```

Then run:
```bash
python prepare_yolo_classify.py
```

This builds:
```
dataset/
  train/<species>/*.jpg
  val/<species>/*.jpg
```

### 2. Train

```bash
python train_yolo.py
```

To reconfigure training (more epochs, bigger model, etc.), edit the parameters inside
`train_yolo.py`:

```python
model = YOLO("yolov8n-cls.pt")   # try "yolov8s-cls.pt" for a bigger/more accurate model

results = model.train(
    data="dataset",
    epochs=50,        # try 100+ for better accuracy
    imgsz=224,         # try 160 for faster training, 320 for more accuracy
    batch=32,          # lower if your machine runs out of memory
    project="spreewald-fish",
    name="yolov8n-cls-baseline",   # change this so re-runs don't overwrite previous results
)
```

Trained weights are saved to:
```
runs/classify/spreewald-fish/<run-name>/weights/best.pt
```

## Notes

- Dataset, trained weights, and run logs are intentionally excluded from this repo
  (`.gitignore`) due to size — keep your local `Fish_Data/`, `dataset/`, and `runs/`
  folders, but don't try to push them.
- Next steps to improve accuracy: more images per species, larger model (`yolov8s`/`m`),
  more epochs, or addressing class imbalance.
