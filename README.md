# AquaPulse Underwater AI & Vision Telemetry System

Welcome to the **AquaPulse** codebase — an automated computer vision and artificial intelligence framework for non-invasive fish detection, species classification, multi-object tracking, and ecological telemetry in underwater environments (such as the Spreewald river network).

---

## 📚 Complete Project Documentation

Detailed documentation and generated reports are available in the [`4 - Documentation/`](file:///C:/Users/parsa/Desktop/Code/4%20-%20Documentation) directory:

1. **Word Document Technical Report**: [`AquaPulse_Preprocessing_and_AI_Process_Report.docx`](file:///C:/Users/parsa/Desktop/Code/4%20-%20Documentation/AquaPulse_Preprocessing_and_AI_Process_Report.docx)
2. **Interactive HTML Workflow & Architecture**: [`AquaPulse_System_Workflow_and_Structure.html`](file:///C:/Users/parsa/Desktop/Code/4%20-%20Documentation/AquaPulse_System_Workflow_and_Structure.html)
3. **Markdown Architecture & Reference Specification**: [`AquaPulse_Workflow_and_Structure.md`](file:///C:/Users/parsa/Desktop/Code/4%20-%20Documentation/AquaPulse_Workflow_and_Structure.md)

---

## 📂 Repository Directory Map

```
C:\Users\parsa\Desktop\Code\
├── 0 - Preprocessing/
│   ├── 0 - Source Codes/
│   │   ├── Extract Frames/          # 1 - all_frames.py, 2 - only_fish_frames.py, 3 - resize.py
│   │   ├── Image dehazing.../      # dehaze-img.py (CUDA MSRCR for single images)
│   │   └── Video dehazing.../      # batch_msrcr_dehaze.py (CUDA MSRCR batch video engine)
│   └── 1 - Insta 360 Process/      # insv_mp4.py (Dual-fisheye to 1080p MP4 conversion)
├── 1 - Training/                   # train_yolo.py, Parsa - yolo + DAT+ DANN + BNN.py
├── 2 - Evaluation/                 # Evaluation scripts & validation metrics
├── 3 - AI process/
│   └── Vision transfromers/        # main.py (Cyberpunk HUD, ViT, MOT, GBIF, Ollama, TTS)
└── 4 - Documentation/              # Word report (.docx), interactive HTML, Markdown docs
```

---

## ⚡ Quick Start & Core Scripts

### 1. Preprocessing Pipeline (`0 - Preprocessing/`)
- **Convert `.insv` 360° videos to rectilinear `.mp4`**:
  ```bash
  python "0 - Preprocessing\1 - Insta 360 Process\insv_mp4.py"
  ```
- **Extract sequential frames**:
  ```bash
  python "0 - Preprocessing\0 - Source Codes\Extract Frames\1 - all_frames.py"
  ```
- **Filter frames with fish objects**:
  ```bash
  python "0 - Preprocessing\0 - Source Codes\Extract Frames\2 - only_fish_frames.py"
  ```
- **Resize to 512x512 (Prevent OOM)**:
  ```bash
  python "0 - Preprocessing\0 - Source Codes\Extract Frames\3 - resize.py"
  ```
- **CUDA MSRCR Video Dehazing**:
  ```bash
  python "0 - Preprocessing\0 - Source Codes\Video dehazing - Color upgrade\batch_msrcr_dehaze.py"
  ```

### 2. Real-Time AI & Telemetry Engine (`3 - AI process/`)
- **Launch Cyberpunk HUD, MOT Tracking & LLM Telemetry**:
  ```bash
  python "3 - AI process\Vision transfromers\main.py"
  ```
