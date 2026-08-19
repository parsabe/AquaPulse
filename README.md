# 🌊 AquaPulse: Robust Computer Vision and Uncertainty Estimation for Aquatic Ecosystems

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch CUDA](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![YOLOv8 Ensemble](https://img.shields.io/badge/YOLO-v8%20Ensemble-00FFFF?style=for-the-badge)](https://github.com/ultralytics/ultralytics)
[![Ollama Llama3](https://img.shields.io/badge/Ollama-Llama--3-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com/)
[![LaTeX Export](https://img.shields.io/badge/LaTeX-PDF%20Engine-008080?style=for-the-badge&logo=latex&logoColor=white)](https://www.miktex.org/)
[![Windows Installer](https://img.shields.io/badge/Windows-Executable%20Setup-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/parsabe/AquaPulse)
[![Docker Container](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

**AquaPulse** is an enterprise-grade, non-invasive artificial intelligence and computer vision framework for real-time aquatic ecosystem telemetry, multi-species fish detection, target tracking, stochastic population estimation, and automated scientific report generation.

Designed for turbid underwater environments (such as the Spreewald river network), AquaPulse fuses deep neural computer vision with stochastic nonlinear data assimilation (Ensemble Kalman Filtering) and local LLM intelligence into a unified real-time dashboard, containerized Docker platform, and automated Windows installation suite.

---

## 🌟 Key Features & Breakthrough Capabilities

### 1. 👁️ Multi-Model YOLO Neural Ensemble & Vision Engine

- **Prioritized Multi-Weight Ensemble**: Simultaneously initializes and runs optimized YOLO weights (`fish_model.pt`, `best.pt`, `meduim.pt`, `small.pt`) with fallback priority loading.
- **Adaptive Contrast Enhancement**: Employs dynamic CLAHE (Contrast Limited Adaptive Histogram Equalization) color restoration in LAB color space for low-visibility, turbid underwater video frames.
- **Cyberpunk Interactive 4-Pane HUD Dashboard**: Native OpenCV window featuring interactive click-and-drag panel divider splitters, target locking/unlocking, live species reticles, and auditory/visual cues.

### 2. 🎯 Multi-Object Tracking & Ecological Census

- **Persistent Track Management**: Integrated BoT-SORT / ByteTrack tracking for frame-to-frame specimen trajectory tracking without double-counting.
- **Dynamic Species Taxonomy**: Live asynchronous REST integration with the **GBIF (Global Biodiversity Information Facility) API** to fetch species taxonomies and high-resolution reference images on specimen target lock.

### 3. 📈 Stochastic Ensemble Kalman Filter (EnKF) Data Assimilation

- **Lotka-Volterra Population Dynamics**: Models prey-predator interaction dynamics governed by:
  $$\frac{dX}{dt} = \alpha X - \beta X Y + \sigma_X dW_X$$
  $$\frac{dY}{dt} = \delta X Y - \gamma Y + \sigma_Y dW_Y$$
- **50-Member Monte Carlo Assimilation**: Continuously updates state priors with live YOLO visual detections, calculating real-time state error covariances, adaptive Kalman gain matrices, and stochastic extinction risk probabilities.
- **20-Plot Analytical Metrics Engine**: Dynamically renders real-time telemetry metrics including:
  - Shannon Diversity Index ($H' = -\sum p_i \ln p_i$) & Pielou's Evenness Metric ($J' = H' / \ln S$)
  - Rayleigh Swimmer Velocity Magnitude Distributions
  - 2D Spatial Centroid Heatmaps & Species Co-occurrence Matrices
  - Population Growth Rate Phase Plots & Extinction Risk Trajectories

### 4. 🤖 Local AI Dialogue Engine (Pauly Assistant)

- **Ollama Llama-3 Integration**: Connects to a local `llama3` LLM via LangChain / Ollama REST endpoints for live marine ecology analysis and situational breakdown.
- **Multilingual Voice Speech Engine**: Integrated TTS system (`pyttsx3`) offering vocal telemetry briefings in English and German.

### 5. 📄 Native LaTeX PDF Exporter

- **Automated Scientific Reports**: Generates 20 high-resolution analytical figures, specimen image crop galleries, and tabular census statistics, injecting them into a standalone LaTeX template (`report_template.tex`) and compiling publication-grade PDF reports via `pdflatex`.

### 6. 📦 Multi-Platform Deployment Options

- **Automated Windows Setup Installer (`AquaPulse_Setup.exe`)**: Deploys application binaries, models, and assets while auditing external prerequisites (**Ollama AI**, `llama3` weights, and **MiKTeX / LaTeX** runtime).
- **Containerized Docker Environment**: Includes Docker container specification for headless execution on GPU clusters or Linux servers.

---

## 📂 Repository Architecture & File Inventory

```
C:\Users\parsa\Desktop\Code\
├── Dockerfile                          # Production PyTorch CUDA + LaTeX Docker container build recipe
├── 0 - Preprocessing/                  # Raw Video & Image Preprocessing Pipeline
│   ├── 0 - Source Codes/
│   │   ├── Extract Frames/             # Frame extraction & 512x512 resolution filters
│   │   ├── Image dehazing.../         # Single-frame CUDA MSRCR dehazing
│   │   └── Video dehazing.../         # Batch video CUDA MSRCR color upgrade
│   └── 1 - Insta 360 Process/         # Dual-fisheye .insv to rectilinear 1080p MP4 conversion
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
│   ├── manual_botsort.py              # BoT-SORT / ByteTrack target tracking module
│   ├── models/                         # YOLO Neural Weights (fish_model.pt, best.pt, etc.)
│   ├── report_template.tex             # Professional LaTeX report document template
│   └── johnny.gif                      # Animated telemetry UI mascot asset
└── 4 - Documentation/                  # Complete system workflow HTML & Word technical reports
```

---

## ⚡ Quick Start & Deployment Options

AquaPulse supports three primary execution modes: **Standalone Windows Setup Installer**, **Containerized Docker Deployment**, and **Developer Mode (Source Execution)**.

---

### Option A: Standalone Windows Setup Installer

The compiled production bundle and automated installer executable are located in:
`C:\Users\parsa\Desktop\New folder`

- **AquaPulse Setup Installer**: [`AquaPulse_Setup.exe`](file:///C:/Users/parsa/Desktop/New%20folder/AquaPulse_Setup.exe)
- **Standalone Application Folder**: [`AquaPulse_App/`](file:///C:/Users/parsa/Desktop/New%20folder/AquaPulse_App)

#### Running the Setup Installer:

Double-click `AquaPulse_Setup.exe` to launch the automated setup wizard. The installer will:

1. Audit and install **Ollama AI Engine** (if not present) and pull the `llama3` neural weights.
2. Audit and install **MiKTeX / LaTeX** (if `pdflatex` is missing) to enable native PDF report compiling.
3. Deploy the application to `C:\AquaPulse` and register a Desktop Shortcut.

---

### Option B: Docker Container Deployment (Headless & GPU Server Setup)

AquaPulse includes a production Docker container configuration for headless GPU clusters, cloud instances, and Linux servers.

#### 1. Build the Docker Image

Build the Docker image locally from the project root:

```bash
docker build -t aquapulse:latest .
```

#### 2. Run Container with NVIDIA GPU Acceleration (Recommended)

Execute with full CUDA acceleration and mount local video and session directories:

```bash
docker run --gpus all -it --rm \
  -v /path/to/videos:/app/data \
  -v /path/to/sessions:/app/video_analysis_sessions \
  -e HEADLESS=1 \
  aquapulse:latest --video /app/data/underwater_stream.mp4
```

#### 3. Run Container in Headless / CPU Mode

For headless servers or CPU execution without GUI display windows:

```bash
docker run -it --rm \
  -v /path/to/videos:/app/data \
  -v /path/to/sessions:/app/video_analysis_sessions \
  aquapulse:latest --video /app/data/underwater_stream.mp4 --headless
```

> [!NOTE]
> - The `--headless` flag or `-e HEADLESS=1` environment variable disables OpenCV GUI display windows, ensuring smooth unattended execution on headless servers.
> - Analysis artifacts (telemetry plots, EnKF state summaries, and compiled LaTeX PDF reports) are written to `/app/video_analysis_sessions/` inside the container and saved directly to the host volume mount.

---

### Option C: Running from Source (Developer Mode)

1. **Activate Virtual Environment**:

   ```powershell
   c:\Users\parsa\Desktop\Code\venv\Scripts\Activate.ps1
   ```

2. **Launch the Master AI Vision Telemetry System**:

   ```powershell
   python "3 - AI process\main.py"
   ```

   _If no video parameter is passed, a native GUI file picker dialog will prompt you to select an underwater video file._

3. **Pass Video Directly via Command Line**:

   ```powershell
   python "3 - AI process\main.py" --video "C:\path\to\underwater_stream.mp4"
   ```

4. **Run in Headless Mode**:

   ```powershell
   python "3 - AI process\main.py" --video "C:\path\to\underwater_stream.mp4" --headless
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

---

## 💻 Tech Stack & Dependencies

- **Deep Learning**: PyTorch, Ultralytics YOLOv8, Vision Transformers (ViT), OpenCV, SciPy, NumPy
- **Data Assimilation**: Ensemble Kalman Filter (EnKF), Euler-Maruyama Stochastic Differential Equations
- **Generative AI & LLM**: Ollama, Llama-3, LangChain, pyttsx3 (SAPI5 Speech API)
- **Deployment & Packaging**: Standalone Windows Executable Setup (`AquaPulse_Setup.exe`), Docker (PyTorch CUDA + LaTeX Container), PyInstaller
- **Publishing & UI**: Native OpenCV 4-Pane Splitter Engine, Matplotlib, LaTeX (`pdflatex`)
