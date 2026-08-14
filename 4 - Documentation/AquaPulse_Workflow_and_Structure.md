# AquaPulse Underwater AI & Vision Telemetry System
## Technical Architecture, Preprocessing Pipeline & AI Process Specification

---

### Executive Summary

The **AquaPulse** system is a specialized computer vision and artificial intelligence ecosystem engineered for automated fish detection, species classification, multi-object tracking, and ecological telemetry in challenging underwater environments (e.g., the Spreewald river network).

Underwater field recordings suffer from severe optical degradation:
- Wavelength-dependent light absorption (red wavelengths decay within ~5 meters).
- Forward scattering causing edge blur and detail loss.
- Backward scattering reducing dynamic contrast.
- Circular fisheye lens distortion from 360° cameras.
- Vast amounts of empty background footage (water, plants, riverbed) introducing dataset noise.

To address these challenges, AquaPulse employs a two-tier modular architecture:
1. **Phase 0 — Preprocessing Pipeline**: Converts raw dual-fisheye 360° videos into standard rectilinear MP4 streams, extracts sequential frames, applies YOLOv8 filtering to isolate frames containing fish, normalizes spatial resolution to 512x512 to prevent VRAM Out-Of-Memory (OOM) failures, and performs Multi-Scale Retinex with Color Restoration (MSRCR) underwater dehazing.
2. **Phase 3 — AI Process & Telemetry Engine**: Integrates YOLOv8, Vision Transformers (ViT), Bayesian Neural Networks (BNN), and Domain Adversarial Neural Networks (DANN) for domain adaptation. Combines ByteTrack multi-object tracking, live GBIF/Wikimedia taxonomy retrieval, a local Ollama LLM telemetry agent (Llama 3 - Dr. Daniel Pauly persona), and multi-lingual voice synthesis with a Cyberpunk HUD interface.

---

## 1. Directory Structure Map

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
└── 4 - Documentation/              # AquaPulse_Preprocessing_and_AI_Process_Report.docx, HTML & MD files
```

---

## 2. Phase 0: Preprocessing Pipeline Breakdown

### 2.1. Dual-Fisheye to Rectilinear MP4 Conversion (`insv_mp4.py`)
Raw recordings from 360° cameras are captured in `.insv` dual-fisheye format with extreme circular lens distortion.
- **Geometric Remapping**: Evaluates left circle center ($cx = W_{in}/4, cy = H_{in}/2$) and radius ($R = H_{in}/2$). Computes focal length $f = \frac{W_{out}/2}{\tan(FOV_x/2)}$ and generates 3D rectilinear ray projections.
- **Equidistant Projection**: Maps rays back to input fisheye coordinates:
  $$r_{fish} = f_{fish} \cdot \theta \quad \text{where } \theta = \arctan \sqrt{x^2 + y^2}, \, f_{fish} = \frac{2R}{\pi}$$
- **CUDA Acceleration**: Grid coordinates in $[-1, 1]$ are passed to PyTorch `torch.nn.functional.grid_sample(..., mode='bilinear', align_corners=True)`, outputting a flat 1920x1080 30FPS MP4 video.

### 2.2. Frame Extraction (`1 - all_frames.py`)
Extracts sequential video frames across input videos using OpenCV `VideoCapture`. Formats output filenames with directory prefixes (e.g., `<prefix>_frame_000123.jpg`) into the `All Frames` directory.

### 2.3. YOLO-Based Fish Frame Filtering (`2 - only_fish_frames.py`)
Raw field footage contains long periods where no fish are in view.
- **Automated Filtering**: Evaluates extracted frames in batches of 32 using CUDA-accelerated YOLOv8 (`yolov8n.pt`).
- **Target Verification**: Only frames with bounding box confidence detections matching target aquatic organisms (`fish` class) are copied to `Extracted fish objects in frames`. Empty background frames are automatically excluded.

### 2.4. Spatial Normalization & 512x512 Resizing to Prevent OOM (`3 - resize.py`)
High-resolution frames (1080p or 4K) cause severe GPU VRAM memory exhaustion during multi-epoch neural training and Vision Transformer self-attention matrix operations, resulting in fatal Out-Of-Memory (OOM) errors.
- **CUDA Tensor Interpolation**: Converts images into PyTorch CUDA float32 tensors and executes bilinear tensor interpolation (`torch.nn.functional.interpolate(tensor, size=(512, 512), mode='bilinear')`).
- **OOM Prevention**: Standardizing inputs to $512 \times 512$ constrains VRAM allocation per batch while preserving critical morphological details (scales, fins, body shape) essential for species classification.

### 2.5. Underwater Image & Video Dehazing — MSRCR Method (`batch_msrcr_dehaze.py`)
To restore visibility and correct underwater color attenuation, AquaPulse implements Multi-Scale Retinex with Color Restoration (MSRCR):
- **Retinex Model**: Decomposes image $I(x,y)$ into illumination $L(x,y)$ and reflectance $R(x,y)$:
  $$I(x,y) = R(x,y) \cdot L(x,y) \implies \log_{10} R(x,y) = \log_{10} I(x,y) - \log_{10} L(x,y)$$
- **Multi-Scale Gaussian Surround**: Blurs across three Gaussian scale sigmas $\sigma \in \{15, 80, 250\}$:
  $$R_{MSR}(x,y) = \frac{1}{3} \sum_{k=1}^{3} \left( \log_{10} I(x,y) - \log_{10} [F_k(x,y) * I(x,y)] \right)$$
- **Color Restoration Factor (CRF)**: Multiplies Retinex by color adjustment weight $C_i(x,y)$:
  $$C_i(x,y) = \log_{10} (125 \cdot I_i(x,y)) - \log_{10} \left( \sum_{j=1}^{C} I_j(x,y) \right)$$
  $$R_{MSRCR, i}(x,y) = C_i(x,y) \cdot R_{MSR, i}(x,y)$$
- **CUDA Acceleration**: Executed using 1D separable Gaussian convolutions on GPU tensors at 30+ FPS while preserving audio tracks via FFmpeg.

> 📌 **RESERVED SECTION FOR DEHAZING OVERRIDES & FIELD LOGS**:
> This area is designated for user calibration logs, water turbidity measurements, camera white-balance overrides, or custom MSRCR hyperparameter settings (custom scale sigmas, color gain factors, clipping bounds).

---

## 3. Phase 3: AI Process & Neural Telemetry Engine

### 3.1. Cyberpunk HUD Telemetry Interface (`main.py`)
Implements real-time computer vision wrapped in a Cyberpunk HUD overlay. Features hardware detection across NVIDIA CUDA, Apple MPS, AMD DirectML, and CPU fallback engines. Renders scanlines, corner reticles, confidence meters, and interactive target locks.

### 3.2. Model Backbones & Domain Adaptation (ViT, BNN, DANN)
- **Vision Transformers (ViT)**: Splits 512x512 fish images into 16x16 visual patches, utilizing self-attention mechanisms to learn fine-grained species patterns (fin structures, body striping).
- **Bayesian Neural Networks (BNN)**: Replaces static linear weights with Gaussian distributions ($\mu, \rho$) using the reparameterization trick. Computes Evidence Lower Bound (ELBO) loss and KL divergence to quantify epistemic uncertainty for rare species.
- **Domain Adversarial Training (DANN)**: Employs a Gradient Reversal Layer (GRL) between the YOLO feature extractor and domain classifier. Reversing gradients ($-\alpha$) forces the backbone to learn domain-invariant representations that bridge clear tank datasets and turbid Spreewald field footage.

### 3.3. Multi-Object Tracking & Target Lock (ByteTrack / BoTSORT)
Integrates Kalman filtering and Hungarian matching (ByteTrack/BoTSORT) to assign persistent track IDs to swimming fish. Includes a sticky target lock mechanism (`update_sticky_target_lock`) with spatial Euclidean distance matching and lost-frame memory buffers to eliminate identity swaps.

### 3.4. GBIF & Wikimedia Taxonomic Knowledge Retrieval
When a target is locked, `main.py` queries the Global Biodiversity Information Facility (GBIF Match & Occurrence API) for scientific taxonomy (Kingdom, Phylum, Class, Order, Family, Genus, Species). Reference photos are fetched from GBIF and Wikimedia Commons, then stored in a persistent local disk cache (`species_snapshots/wiki_cache/`) for offline operation.

### 3.5. Local LLM Telemetry Agent (Ollama LLM - Llama 3) & Multi-Lingual Voice Synthesis
AquaPulse integrates a local LLM agent via Ollama (Llama 3) assuming the persona of marine biologist Dr. Daniel Pauly. The LLM synthesizes GBIF taxonomy into concise scientific explanations capped at 40 words. Voice output is rendered by `CancellableAudioEngine` (pyttsx3) in English or German, equipped with mutual exclusion locks to prevent speech overlap.

---

## 4. System Pipeline & Workflow Summary Table

| Stage | Script / Module | Core Technology | Primary Function |
|---|---|---|---|
| **0.1 INSV Conversion** | `insv_mp4.py` | PyTorch grid_sample (CUDA) | Dual-fisheye 360° to 1080p MP4 conversion |
| **0.2 Frame Extract** | `1 - all_frames.py` | OpenCV VideoCapture | Sequential frame extraction across video files |
| **0.3 Fish Filtering** | `2 - only_fish_frames.py` | YOLOv8 Object Detection | Isolates frames containing fish; strips empty frames |
| **0.4 Spatial Resize** | `3 - resize.py` | PyTorch CUDA Tensor Interpolation | Normalizes frames to 512x512 to prevent GPU OOM |
| **0.5 MSRCR Dehazing** | `batch_msrcr_dehaze.py` | Multi-Scale Retinex (CUDA) | Underwater haze removal & color upgrade |
| **3.0 AI Telemetry** | `main.py` | ViT + BNN + DANN + ByteTrack + Ollama | Real-time tracking, GBIF taxonomy & voice HUD |

---

## 5. Comprehensive Scientific References

1. **Jobson, D. J., Rahman, Z. U., & Woodell, G. A. (1997).** *A multiscale retinex for bridging the gap between color automatic images and the visual appearance of scenes.* IEEE Transactions on Image Processing, 6(7), 965-976.
2. **Land, E. H., & McCann, J. J. (1971).** *Lightness and Retinex theory.* Journal of the Optical Society of America, 61(1), 1-11.
3. **Jocher, G., Chaurasia, A., & Qiu, J. (2023).** *Ultralytics YOLOv8 (Version 8.0.0).* GitHub. https://github.com/ultralytics/ultralytics
4. **Dosovitskiy, A., et al. (2020).** *An image is worth 16x16 words: Transformers for image recognition at scale.* arXiv preprint arXiv:2010.11929.
5. **Ganin, Y., et al. (2016).** *Domain-adversarial training of neural networks.* Journal of Machine Learning Research, 17(59), 1-35.
6. **Blundell, C., Cornebise, J., Kavukcuoglu, K., & Wierstra, D. (2015).** *Weight uncertainty in neural network.* ICML, 1613-1622.
7. **Zhang, Y., et al. (2022).** *ByteTrack: Multi-object tracking by associating every detection box.* ECCV, 1-21.
8. **Ancuti, C. O., Ancuti, C., Haber, T., & Bekaert, P. (2012).** *Enhancing underwater images and videos by fusion.* IEEE CVPR, 81-88.
9. **GBIF Secretariat. (2026).** *GBIF Backbone Taxonomy.* GBIF REST API. https://api.gbif.org/v1/species/match
10. **Touvron, H., et al. (2023).** *Llama 2 / Llama 3: Open foundation and fine-tuned chat models.* Meta AI.
