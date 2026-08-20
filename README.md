# 🌊 AquaPulse: Robust Computer Vision, BotSORT Tracking, and Stochastic Uncertainty Estimation for Aquatic Ecosystems

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flutter Android](https://img.shields.io/badge/Flutter-Android%20App-02569B?style=for-the-badge&logo=flutter&logoColor=white)](https://flutter.dev/)
[![PyTorch CUDA](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![YOLOv8 Ensemble](https://img.shields.io/badge/YOLO-v8%20Ensemble-00FFFF?style=for-the-badge)](https://github.com/ultralytics/ultralytics)
[![BotSORT Tracker](https://img.shields.io/badge/BotSORT-CMC%20%2B%20Re--ID-FF6F00?style=for-the-badge)](https://github.com/Nvidia/DeepStream-Yolo)
[![Ollama Llama3](https://img.shields.io/badge/Ollama-Llama--3-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com/)
[![Cloud LaTeX Export](https://img.shields.io/badge/Cloud%20LaTeX-PDF%20Engine-008080?style=for-the-badge&logo=latex&logoColor=white)](https://latex.online/)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-parsabe99%2Faquapulse--ai%3Alatest-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://hub.docker.com/r/parsabe99/aquapulse-ai)
[![Official Website](https://img.shields.io/badge/Website-aquapulse.ai-10B981?style=for-the-badge&logo=googlechrome&logoColor=white)](https://aquapulse.ai)

**AquaPulse** is an enterprise-grade, non-invasive artificial intelligence and computer vision framework for real-time aquatic ecosystem telemetry, multi-species fish detection, BotSORT target tracking, stochastic population estimation, and automated Cloud LaTeX scientific report generation.

Designed for turbid underwater environments (such as the Spreewald river network), AquaPulse fuses deep neural computer vision with stochastic nonlinear data assimilation (Ensemble Kalman Filtering), local LLM intelligence, a cross-platform **Flutter Android Mobile Application**, a containerized **Docker Hub distribution**, and an automated Windows installation suite.

---

## 🌐 Official Website

https://aquapulse.ai

---

## 🌟 Key Features & Breakthrough Capabilities

### 1. 📱 Cross-Platform Mobile Android Application (Flutter)

Located in [`App/`](file:///c:/Users/parsa/Desktop/Code/App), the AquaPulse Android mobile app features:
- **Dynamic YouTube & Gallery Video Attachments**: Attach local field video files (`.mp4`, `.mov`) or paste YouTube URLs (e.g. `https://www.youtube.com/watch?v=kxSjkyoW3WM`) to run optical stream decoding and target tracking.
- **BotSORT Multi-Object Tracker (CMC + Extended Kalman + Re-ID)**: Applied Camera Motion Compensation (CMC), Kalman Filter state updates, and appearance Re-ID feature matrix verification.
- **Video Control Toolbar**: Includes `-10s` rewind, `+10s` fast-forward, play/pause frame freeze inspection, stop, loop toggle, and interactive timestamp progress scrubber (`01:42 / 05:30`).
- **Johnny Silverhand Relic Glitch System**: Cyberpunk full-screen overlay with periodic 30s neural engram triggers, TTS spoken voice quotes (`pitch = 0.82`), RGB split chromatic distortion, and local single-pass GIF avatar.
- **Dr. Pauly Voice Portal & Fish Photo Attachment**: Interactive Ollama LLM biological assistant with multi-paragraph species analyses, fish photo attachment inspection modal, TTS voice synthesis (`🔊`), and auto-scrolling chat history.
- **20-Plot Analytical Telemetry Suite**: Real-time rendering of Lotka-Volterra phase orbits, Monte Carlo extinction risk curves (>35% alarm threshold), Shannon diversity indices ($H'$), and hydroacoustic sound pressure ($148.5\,\text{dB re } 1\,\mu\text{Pa}$).
- **Cloud LaTeX Report Generator & PDF Archive**: Generates per-video `.tex` source code, compiles PDF reports via Cloud LaTeX Compiler API (`latex.online`), and provides saved report management with deletion options.

### 2. 👁️ Multi-Model YOLO Neural Ensemble & Vision Engine

- **Prioritized Multi-Weight Ensemble**: Simultaneously initializes and runs optimized YOLO weights (`fish_model.pt`, `best.pt`, `meduim.pt`, `small.pt`) with fallback priority loading.
- **Adaptive Contrast Enhancement**: Employs dynamic CLAHE (Contrast Limited Adaptive Histogram Equalization) color restoration in LAB color space for low-visibility, turbid underwater video frames.
- **Cyberpunk Interactive 4-Pane HUD Dashboard**: Native OpenCV window featuring interactive click-and-drag panel divider splitters, target locking/unlocking, live species reticles, and auditory/visual cues.

### 3. 🎯 BotSORT Multi-Object Tracking & Ecological Census

- **Persistent Track Management**: Integrated BotSORT (Camera Motion Compensation + Extended Kalman Filtering + Re-ID) and ByteTrack for frame-to-frame specimen trajectory tracking without double-counting.
- **Dynamic Species Taxonomy**: Live asynchronous REST integration with the **GBIF (Global Biodiversity Information Facility) API** to fetch species taxonomies and high-resolution reference images on specimen target lock.

### 4. 📈 Stochastic Ensemble Kalman Filter (EnKF) Data Assimilation

- **Lotka-Volterra Population Dynamics**: Models prey-predator interaction dynamics governed by:
  $$\frac{dX}{dt} = \alpha X - \beta X Y + \sigma_X dW_X$$
  $$\frac{dY}{dt} = \delta X Y - \gamma Y + \sigma_Y dW_Y$$
- **50-Member Monte Carlo Assimilation**: Continuously updates state priors with live YOLO visual detections, calculating real-time state error covariances, adaptive Kalman gain matrices, and stochastic extinction risk probabilities.
- **20-Plot Analytical Metrics Engine**: Dynamically renders real-time telemetry metrics including:
  - Shannon Diversity Index ($H' = -\sum p_i \ln p_i$) & Pielou's Evenness Metric ($J' = H' / \ln S$)
  - Rayleigh Swimmer Velocity Magnitude Distributions
  - 2D Spatial Centroid Heatmaps & Species Co-occurrence Matrices
  - Population Growth Rate Phase Plots & Extinction Risk Trajectories

### 5. 🤖 Local AI Dialogue Engine (Pauly Assistant)

- **Ollama Llama-3 Integration**: Connects to a local `llama3` LLM via LangChain / Ollama REST endpoints for live marine ecology analysis and situational breakdown.
- **Multilingual Voice Speech Engine**: Integrated TTS system (`flutter_tts` / `pyttsx3`) offering vocal telemetry briefings.

### 6. 📄 Per-Video Cloud LaTeX PDF Exporter

- **Automated Scientific Reports**: Generates per-video LaTeX source code (`.tex`) with bioacoustic equations and BotSORT tables, compiling publication-grade PDF reports via Cloud LaTeX Compiler API (`latex.online`).

---

## 🐳 Docker Hub Distribution

The official pre-built AquaPulse Docker image is published on Docker Hub:

```bash
docker pull parsabe99/aquapulse-ai:latest
```

### Run Container with NVIDIA GPU Acceleration (Recommended)

```bash
docker run --gpus all -it --rm \
  -v /path/to/videos:/app/data \
  -v /path/to/sessions:/app/video_analysis_sessions \
  -e HEADLESS=1 \
  parsabe99/aquapulse-ai:latest --video /app/data/underwater_stream.mp4
```

### Run Container in Headless / CPU Mode

```bash
docker run -it --rm \
  -v /path/to/videos:/app/data \
  -v /path/to/sessions:/app/video_analysis_sessions \
  parsabe99/aquapulse-ai:latest --video /app/data/underwater_stream.mp4 --headless
```

---

## 📂 Repository Architecture & File Inventory

```
C:\Users\parsa\Desktop\Code\
├── Dockerfile                          # Production PyTorch CUDA + LaTeX Docker container build recipe
├── App/                                # Cross-Platform Flutter Android Mobile Application
│   ├── lib/
│   │   ├── main.dart                   # Flutter app entry point & Riverpod scope
│   │   ├── views/
│   │   │   ├── live_camera_viewer_screen.dart   # Live Stream, BotSORT Tracker, YouTube link, video controls
│   │   │   ├── offline_taxonomy_screen.dart     # GBIF offline species taxonomy lookup
│   │   │   ├── ecological_risk_alarm_screen.dart# 20-plot fl_chart telemetry suite & alarm triggers
│   │   │   ├── acousto_visual_sde_screen.dart   # Hydroacoustics & Neural SDE trajectory forecasting
│   │   │   ├── dr_pauly_voice_portal_screen.dart# Ollama voice assistant, fish photo upload & TTS
│   │   │   ├── profile_reports_screen.dart      # Field Profile, Cloud LaTeX PDF compiler & report archive
│   │   │   └── main_navigation_screen.dart      # Bottom navigation bar & Johnny FAB trigger
│   │   ├── widgets/
│   │   │   ├── johnny_glitch_overlay.dart       # Johnny Silverhand full-screen Cyberpunk glitch overlay
│   │   │   └── glass_container.dart             # Glassmorphic UI container
│   │   ├── services/
│   │   │   ├── ollama_voice_service.dart        # Ollama LLM API client & vision inspection
│   │   │   └── gbif_taxonomy_service.dart       # GBIF REST API client
│   │   ├── providers/                       # Riverpod state providers
│   │   └── models/                          # Telemetry & specimen data models
│   ├── assets/
│   │   └── johnny.gif                   # Johnny Silverhand local GIF asset
│   └── pubspec.yaml                     # Flutter dependencies & asset declarations
├── 0 - Preprocessing/                  # Raw Video & Image Preprocessing Pipeline
├── 1 - Training/                       # YOLO model training, DANN domain adaptation, BNN
├── 2 - Evaluation/                     # Validation scripts, precision-recall & mAP evaluation
├── 3 - AI process/                     # Core AquaPulse AI Telemetry Engine
│   ├── main.py                         # Master entry point & 4-Pane interactive OpenCV HUD
│   ├── mod_00_config_and_assets.py     # Hardware GPU/CPU detection & asset management
│   ├── mod_01_eco_census.py            # Species census enumeration & telemetry tracking
│   ├── mod_02_stochastic_enkf.py       # 50-member Ensemble Kalman Filter engine
│   ├── mod_03_chart_renderer.py        # Real-time 20-plot Matplotlib rendering engine
│   ├── mod_04_vision_engine.py         # Multi-model YOLO ensemble & CLAHE dehazing
│   ├── mod_05_dialogue_and_ollama.py   # Ollama Llama3 LLM assistant & pyttsx3 voice engine
│   ├── mod_06_ui_dashboard.py          # Dashboard HUD layout & interactive prompt dialogs
│   ├── mod_07_pdf_exporter.py          # Native LaTeX template engine & pdflatex compiler
│   ├── manual_botsort.py              # BotSORT / ByteTrack target tracking module
│   ├── models/                         # YOLO Neural Weights (fish_model.pt, best.pt, etc.)
│   └── johnny.gif                      # Animated telemetry UI mascot asset
└── 4 - Documentation/                  # Complete system workflow HTML & Word technical reports
```

---

## ⚡ Quick Start & Deployment Options

AquaPulse supports four primary execution modes: **Flutter Android Mobile App**, **Docker Hub Container (`parsabe99/aquapulse-ai:latest`)**, **Standalone Windows Setup Installer**, and **Developer Source Execution**.

---

### Option A: Flutter Android Mobile Application

1. Open `App/` in Flutter / Android Studio:
   ```bash
   cd App
   flutter pub get
   ```
2. Run on Android Emulator or connected phone:
   ```bash
   flutter run
   ```
3. Test production build:
   ```bash
   flutter test
   ```

---

### Option B: Docker Hub Deployment (`parsabe99/aquapulse-ai:latest`)

Pull and run the official Docker Hub image:

```bash
docker pull parsabe99/aquapulse-ai:latest

docker run --gpus all -it --rm \
  -v /path/to/videos:/app/data \
  -v /path/to/sessions:/app/video_analysis_sessions \
  -e HEADLESS=1 \
  parsabe99/aquapulse-ai:latest --video /app/data/underwater_stream.mp4
```

---

### Option C: Standalone Windows Setup Installer

The compiled production bundle and automated installer executable are located in:
`C:\Users\parsa\Desktop\New folder`

- **AquaPulse Setup Installer**: [`AquaPulse_Setup.exe`](file:///C:/Users/parsa/Desktop/New%20folder/AquaPulse_Setup.exe)
- **Standalone Application Folder**: [`AquaPulse_App/`](file:///C:/Users/parsa/Desktop/New%20folder/AquaPulse_App)

---

### Option D: Running from Source (Developer Mode)

1. **Activate Virtual Environment**:

   ```powershell
   c:\Users\parsa\Desktop\Code\venv\Scripts\Activate.ps1
   ```

2. **Launch the Master AI Vision Telemetry System**:

   ```powershell
   python "3 - AI process\main.py"
   ```

---

## 🔬 System Telemetry & Output Session Structure

Each video analysis session generates an isolated, timestamped output bundle under `video_analysis_sessions/`:

```
video_analysis_sessions/<video_name>_<timestamp>/
├── output/           # Processed MP4 video with target reticles & EnKF HUD overlays
├── csv/              # Raw specimen counts and track data per frame
├── plots/            # 20 high-resolution analytical PNG telemetry plots
└── analysis/         # Ollama AI narrative report (.md), generated .tex file, and compiled PDF report
```

---

## 📄 Complete Project Documentation

For exhaustive mathematical details, system design diagrams, and empirical results, view:

1. **Word Document Technical Report**: [`4 - Documentation/AquaPulse_Preprocessing_and_AI_Process_Report.docx`](file:///C:/Users/parsa/Desktop/Code/4%20-%20Documentation/AquaPulse_Preprocessing_and_AI_Process_Report.docx)
2. **Interactive HTML Workflow & Architecture**: [`4 - Documentation/AquaPulse_System_Workflow_and_Structure.html`](file:///C:/Users/parsa/Desktop/Code/4%20-%20Documentation/AquaPulse_System_Workflow_and_Structure.html)
3. **Markdown Architecture & Reference Specification**: [`4 - Documentation/AquaPulse_Workflow_and_Structure.md`](file:///C:/Users/parsa/Desktop/Code/4%20-%20Documentation/AquaPulse_Workflow_and_Structure.md)
