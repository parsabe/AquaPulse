#!/usr/bin/env bash
# ==============================================================================
#  🌊 AquaPulse AI - Single-File Debian (.deb) Package Builder
# ==============================================================================
#  This standalone shell script packages the entire AquaPulse AI Vision Kernel,
#  pre-trained YOLO neural models (fish_model.pt, best.pt, meduim.pt, small.pt),
#  telemetry assets, documentation, launcher scripts, and desktop integration
#  into strictly ONE SINGLE .deb package file.
# ==============================================================================

set -euo pipefail

# --- COLOR DEFINITIONS ---
BOLD="\033[1m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

log_info()  { echo -e "${CYAN}[INFO]${RESET} $*"; }
log_ok()    { echo -e "${GREEN}[OK]${RESET} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${RESET} $*"; }
log_error() { echo -e "${RED}[ERROR]${RESET} $*" >&2; }

# --- SCRIPT & DIRECTORY DETECTION ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# --- CONFIGURATION ---
PKG_NAME="aquapulse"
PKG_VERSION="1.0.0"
PKG_ARCH="$(dpkg --print-architecture 2>/dev/null || uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')"
TARGET_DIR="${1:-"${SCRIPT_DIR}/dist"}"
DEB_FILENAME="${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}.deb"
FINAL_DEB="${TARGET_DIR}/${DEB_FILENAME}"

echo -e "${BOLD}${CYAN}========================================================================"
echo "  🌊 AquaPulse: Single-File Debian (.deb) Package Build Pipeline"
echo "========================================================================${RESET}"
echo "  Workspace Directory : ${SCRIPT_DIR}"
echo "  Target Output Dir   : ${TARGET_DIR}"
echo "  Package Filename    : ${DEB_FILENAME}"
echo "  Architecture        : ${PKG_ARCH}"
echo "========================================================================"

# --- 1. AUDIT PREREQUISITES ---
log_info "[Step 1/6] Auditing system tools, models, and kernel assets..."

if ! command -v dpkg-deb >/dev/null 2>&1; then
    log_error "dpkg-deb is not installed. Please install dpkg-dev or dpkg."
    exit 1
fi
log_ok "Detected Debian package builder: $(command -v dpkg-deb)"

if ! command -v python3 >/dev/null 2>&1; then
    log_error "python3 is required to build the package."
    exit 1
fi
log_ok "Detected Python interpreter: $(command -v python3) ($(python3 --version))"

# Check YOLO models
MODELS_DIR="${SCRIPT_DIR}/models"
EXPECTED_MODELS=("fish_model.pt" "best.pt" "meduim.pt" "small.pt")

if [ ! -d "${MODELS_DIR}" ]; then
    log_error "Models directory '${MODELS_DIR}' not found!"
    exit 1
fi

for model in "${EXPECTED_MODELS[@]}"; do
    model_path="${MODELS_DIR}/${model}"
    if [ ! -f "${model_path}" ]; then
        log_error "Required neural weight missing: ${model_path}"
        exit 1
    fi
    size_mb=$(du -m "${model_path}" | cut -f1)
    log_ok "Verified YOLO model : $(printf '%-20s' "${model}") (${size_mb} MB)"
done

# Check core kernel assets
KERNEL_DIR="${SCRIPT_DIR}/kernel"
AI_PROCESS_DIR="${KERNEL_DIR}/3 - AI process"

if [ ! -d "${AI_PROCESS_DIR}" ]; then
    log_error "Kernel AI process directory '${AI_PROCESS_DIR}' not found!"
    exit 1
fi

EXPECTED_ASSETS=(
    "main.py"
    "mod_00_config_and_assets.py"
    "mod_01_eco_census.py"
    "mod_02_stochastic_enkf.py"
    "mod_03_chart_renderer.py"
    "mod_04_vision_engine.py"
    "mod_05_dialogue_and_ollama.py"
    "mod_06_ui_dashboard.py"
    "mod_07_pdf_exporter.py"
    "manual_botsort.py"
    "johnny.gif"
    "report_template.tex"
    "aquapulse_system_architecture_documentation.tex"
    "app_icon.ico"
)

for asset in "${EXPECTED_ASSETS[@]}"; do
    asset_path="${AI_PROCESS_DIR}/${asset}"
    if [ ! -f "${asset_path}" ]; then
        log_error "Required kernel asset missing: ${asset_path}"
        exit 1
    fi
    log_ok "Verified kernel file: ${asset}"
done

# --- 2. PREPARE CLEAN ISOLATED STAGING DIRECTORY ---
log_info "[Step 2/6] Initializing isolated staging rootfs..."
STAGING_DIR="$(mktemp -d -t aquapulse_deb_stage_XXXXXX)"

cleanup() {
    if [ -d "${STAGING_DIR}" ]; then
        rm -rf "${STAGING_DIR}"
    fi
}
trap cleanup EXIT ERR INT TERM

# Structure standard Linux system paths
mkdir -p "${STAGING_DIR}/DEBIAN"
mkdir -p "${STAGING_DIR}/opt/aquapulse/models"
mkdir -p "${STAGING_DIR}/opt/aquapulse/kernel"
mkdir -p "${STAGING_DIR}/usr/bin"
mkdir -p "${STAGING_DIR}/usr/share/applications"
mkdir -p "${STAGING_DIR}/usr/share/pixmaps"
mkdir -p "${STAGING_DIR}/usr/share/icons/hicolor"
mkdir -p "${STAGING_DIR}/usr/share/doc/aquapulse"

log_ok "Staging environment created at: ${STAGING_DIR}"

# --- 3. COPY PAYLOAD & POPULATE DIRECTORIES ---
log_info "[Step 3/6] Packaging kernel suite and YOLO neural models..."

# Copy neural weights
cp -r "${MODELS_DIR}"/* "${STAGING_DIR}/opt/aquapulse/models/"

# Copy entire kernel (excluding git cache and temp files)
cp -r "${KERNEL_DIR}"/* "${STAGING_DIR}/opt/aquapulse/kernel/"
find "${STAGING_DIR}/opt/aquapulse/kernel" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${STAGING_DIR}/opt/aquapulse/kernel" -type f -name "*.pyc" -delete 2>/dev/null || true

# Symlink models directly inside 'kernel/3 - AI process/models' and 'kernel/models'
# to satisfy all relative path resolutions (e.g., os.path.join(script_dir, "models"))
ln -s "../../models" "${STAGING_DIR}/opt/aquapulse/kernel/3 - AI process/models"
ln -s "../models" "${STAGING_DIR}/opt/aquapulse/kernel/models"

# Copy root requirements and documentation
if [ -f "${KERNEL_DIR}/requirements.txt" ]; then
    cp "${KERNEL_DIR}/requirements.txt" "${STAGING_DIR}/opt/aquapulse/requirements.txt"
fi
if [ -f "${KERNEL_DIR}/req.txt" ]; then
    cp "${KERNEL_DIR}/req.txt" "${STAGING_DIR}/opt/aquapulse/req.txt"
fi
if [ -f "${SCRIPT_DIR}/README.md" ]; then
    cp "${SCRIPT_DIR}/README.md" "${STAGING_DIR}/usr/share/doc/aquapulse/README.md"
    cp "${SCRIPT_DIR}/README.md" "${STAGING_DIR}/opt/aquapulse/README.md"
fi

# Pre-create runtime directories with full write access for non-root users
mkdir -p "${STAGING_DIR}/opt/aquapulse/kernel/3 - AI process/video_analysis_sessions"
mkdir -p "${STAGING_DIR}/opt/aquapulse/kernel/3 - AI process/output"

log_ok "Bundled models (~$(du -sh "${MODELS_DIR}" | cut -f1)) and kernel (~$(du -sh "${KERNEL_DIR}" | cut -f1)) into /opt/aquapulse"

# --- 4. DESKTOP INTEGRATION, ICONS & LAUNCHER ---
log_info "[Step 4/6] Creating desktop shortcuts, high-res icons, and launcher..."

# Extract icon from app_icon.ico using Python Pillow
python3 - <<EOF
import os
from PIL import Image

ico_path = "${AI_PROCESS_DIR}/app_icon.ico"
pixmap_path = "${STAGING_DIR}/usr/share/pixmaps/aquapulse.png"

try:
    with Image.open(ico_path) as img:
        img.save(pixmap_path, format="PNG")
        for size in [16, 32, 48, 64, 128, 256]:
            icon_dir = f"${STAGING_DIR}/usr/share/icons/hicolor/{size}x{size}/apps"
            os.makedirs(icon_dir, exist_ok=True)
            res = img.resize((size, size), Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS)
            res.save(os.path.join(icon_dir, "aquapulse.png"), format="PNG")
    print("  [OK] Converted and installed multi-resolution application icons.")
except Exception as e:
    print(f"  [WARN] Note during icon conversion: {e}")
EOF

# Copy app_icon.ico into /opt/aquapulse
cp "${AI_PROCESS_DIR}/app_icon.ico" "${STAGING_DIR}/opt/aquapulse/app_icon.ico"

# Create /usr/bin/aquapulse executable launcher
cat <<'EOF' > "${STAGING_DIR}/usr/bin/aquapulse"
#!/usr/bin/env bash
# ==============================================================================
#  🌊 AquaPulse AI Telemetry & Vision Engine - Official Linux Launcher
# ==============================================================================
set -e

APP_ROOT="/opt/aquapulse"
KERNEL_DIR="${APP_ROOT}/kernel/3 - AI process"
MAIN_SCRIPT="${KERNEL_DIR}/main.py"

# Banner
echo "========================================================================"
echo "  🌊 AquaPulse: AI Vision, BotSORT & Stochastic EnKF Telemetry Engine"
echo "========================================================================"

if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] python3 is required to run AquaPulse." >&2
    exit 1
fi

# Ensure output and sessions directories are writable
if [ -w "${KERNEL_DIR}" ]; then
    mkdir -p "${KERNEL_DIR}/video_analysis_sessions" "${KERNEL_DIR}/output" 2>/dev/null || true
fi

# Check Python environment dependencies
PYTHON_CMD="python3"
check_env() {
    "$1" -c "import torch, ultralytics, cv2, numpy, scipy" >/dev/null 2>&1
}

if check_env "python3"; then
    PYTHON_CMD="python3"
elif [ -f "${APP_ROOT}/.venv/bin/python3" ] && check_env "${APP_ROOT}/.venv/bin/python3"; then
    PYTHON_CMD="${APP_ROOT}/.venv/bin/python3"
elif [ -f "${HOME}/.local/share/aquapulse/venv/bin/python3" ] && check_env "${HOME}/.local/share/aquapulse/venv/bin/python3"; then
    PYTHON_CMD="${HOME}/.local/share/aquapulse/venv/bin/python3"
else
    # Auto-initialize user virtual environment on first launch
    USER_VENV="${HOME}/.local/share/aquapulse/venv"
    echo ""
    echo "[INFO] AquaPulse core dependencies (torch, ultralytics) not detected in global environment."
    echo "[INFO] Initializing dedicated virtual environment at:"
    echo "       ${USER_VENV}"
    echo ""
    mkdir -p "$(dirname "${USER_VENV}")"
    if [ ! -d "${USER_VENV}" ]; then
        python3 -m venv --system-site-packages "${USER_VENV}"
    fi
    echo "[INFO] Installing required neural packages (PyTorch, Ultralytics, OpenCV)..."
    "${USER_VENV}/bin/pip" install --upgrade pip
    if [ -f "${APP_ROOT}/requirements.txt" ]; then
        "${USER_VENV}/bin/pip" install -r "${APP_ROOT}/requirements.txt"
    fi
    if [ -f "${APP_ROOT}/req.txt" ]; then
        "${USER_VENV}/bin/pip" install -r "${APP_ROOT}/req.txt"
    fi
    PYTHON_CMD="${USER_VENV}/bin/python3"
    echo "[OK] Environment initialization complete!"
    echo ""
fi

# Pass all CLI arguments directly to the AquaPulse AI engine
exec "${PYTHON_CMD}" "${MAIN_SCRIPT}" "$@"
EOF
chmod 755 "${STAGING_DIR}/usr/bin/aquapulse"

# Alias techno-eco-project to aquapulse
ln -s "aquapulse" "${STAGING_DIR}/usr/bin/techno-eco-project"

# Create /usr/share/applications/aquapulse.desktop
cat <<EOF > "${STAGING_DIR}/usr/share/applications/aquapulse.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=AquaPulse AI
GenericName=Underwater Ecosystem Telemetry & Vision Engine
Comment=Robust Computer Vision, BotSORT Tracking, and Stochastic Uncertainty Estimation for Aquatic Ecosystems
Exec=/usr/bin/aquapulse %F
Icon=aquapulse
Terminal=true
Categories=Science;AudioVideo;Video;ArtificialIntelligence;DataVisualization;
MimeType=video/mp4;video/x-matroska;video/x-msvideo;video/quicktime;
StartupNotify=true
Keywords=aquapulse;yolo;botsort;enkf;telemetry;fish;marine;underwater;
EOF
chmod 644 "${STAGING_DIR}/usr/share/applications/aquapulse.desktop"

# Symlink techno-eco-project.desktop
ln -s "aquapulse.desktop" "${STAGING_DIR}/usr/share/applications/techno-eco-project.desktop"

# Copy copyright information
cat <<EOF > "${STAGING_DIR}/usr/share/doc/aquapulse/copyright"
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: AquaPulse
Upstream-Contact: AquaPulse AI Team <contact@aquapulse.ai>
Source: https://github.com/parsabe/AquaPulse

Files: *
Copyright: 2026 AquaPulse AI Team
License: MIT
EOF
chmod 644 "${STAGING_DIR}/usr/share/doc/aquapulse/copyright"

# --- 5. DEBIAN CONTROL SPECIFICATION & SCRIPTS ---
log_info "[Step 5/6] Generating Debian package control specifications and maintainer scripts..."

INSTALLED_SIZE_KB=$(du -sk --exclude=DEBIAN "${STAGING_DIR}" | cut -f1)

cat <<EOF > "${STAGING_DIR}/DEBIAN/control"
Package: ${PKG_NAME}
Version: ${PKG_VERSION}
Section: science
Priority: optional
Architecture: ${PKG_ARCH}
Installed-Size: ${INSTALLED_SIZE_KB}
Maintainer: AquaPulse AI Team <contact@aquapulse.ai>
Depends: python3 (>= 3.8), python3-pip, python3-venv, python3-tk, ffmpeg, libgl1, libglib2.0-0
Recommends: curl, git, ollama
Suggests: texlive-latex-base, texlive-latex-extra, texlive-fonts-recommended
Homepage: https://aquapulse.ai
Description: Robust Computer Vision & EnKF Telemetry for Aquatic Ecosystems
 AquaPulse is an enterprise-grade AI and computer vision framework for
 real-time aquatic ecosystem telemetry, multi-species fish detection,
 BotSORT tracking, stochastic population estimation (EnKF), and automated
 scientific Cloud LaTeX report generation.
 .
 Bundles pre-trained YOLO neural weights (fish_model.pt, best.pt, meduim.pt, small.pt).
EOF
chmod 644 "${STAGING_DIR}/DEBIAN/control"

# Post-installation script
cat <<'EOF' > "${STAGING_DIR}/DEBIAN/postinst"
#!/bin/sh
set -e

# Fix ownership and permissions for /opt/aquapulse
chmod -R 755 /opt/aquapulse

# Allow unprivileged users to write session logs, plots and output videos
if [ -d "/opt/aquapulse/kernel/3 - AI process" ]; then
    mkdir -p "/opt/aquapulse/kernel/3 - AI process/video_analysis_sessions"
    mkdir -p "/opt/aquapulse/kernel/3 - AI process/output"
    chmod 777 "/opt/aquapulse/kernel/3 - AI process/video_analysis_sessions" 2>/dev/null || true
    chmod 777 "/opt/aquapulse/kernel/3 - AI process/output" 2>/dev/null || true
fi

# Update desktop application registry and icon cache
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications 2>/dev/null || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor 2>/dev/null || true
fi

echo ""
echo "========================================================================"
echo "  [SUCCESS] AquaPulse AI has been successfully installed!"
echo "  Launch the application from your desktop menu or terminal:"
echo "      aquapulse [optional_video_path.mp4]"
echo "========================================================================"
echo ""

exit 0
EOF
chmod 755 "${STAGING_DIR}/DEBIAN/postinst"

# Post-removal script
cat <<'EOF' > "${STAGING_DIR}/DEBIAN/postrm"
#!/bin/sh
set -e

if [ "$1" = "remove" ] || [ "$1" = "purge" ]; then
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database -q /usr/share/applications 2>/dev/null || true
    fi
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor 2>/dev/null || true
    fi
fi

if [ "$1" = "purge" ]; then
    rm -rf /opt/aquapulse 2>/dev/null || true
fi

exit 0
EOF
chmod 755 "${STAGING_DIR}/DEBIAN/postrm"

# Fix overall staging permissions
find "${STAGING_DIR}" -type d -exec chmod 755 {} +
find "${STAGING_DIR}" -type f -exec chmod 644 {} +
chmod 755 "${STAGING_DIR}/DEBIAN/postinst" "${STAGING_DIR}/DEBIAN/postrm"
chmod 755 "${STAGING_DIR}/usr/bin/aquapulse"

# --- 6. COMPILE & DEPLOY STRICTLY ONE SINGLE .DEB FILE ---
log_info "[Step 6/6] Building standalone single .deb archive via dpkg-deb..."

mkdir -p "${TARGET_DIR}"

# Wipe any previous contents in target directory to guarantee strictly ONLY ONE single file exists
for item in "${TARGET_DIR}"/*; do
    if [ -e "${item}" ]; then
        rm -rf "${item}"
    fi
done

# Build .deb with root ownership mapping
dpkg-deb --build --root-owner-group "${STAGING_DIR}" "${FINAL_DEB}"

# Verify build
if [ ! -f "${FINAL_DEB}" ]; then
    log_error "Debian package build failed: ${FINAL_DEB} was not generated."
    exit 1
fi

DEB_SIZE_MB=$(du -m "${FINAL_DEB}" | cut -f1)
DEB_SHA256=$(sha256sum "${FINAL_DEB}" | awk '{print $1}')
FINAL_COUNT=$(find "${TARGET_DIR}" -mindepth 1 -maxdepth 1 | wc -l)

echo ""
echo -e "${BOLD}${GREEN}========================================================================"
echo "  [SUCCESS] ONLY AND ONLY ONE .DEB FILE CREATED!"
echo "========================================================================${RESET}"
echo "  Package Path : ${FINAL_DEB}"
echo "  File Size    : ${DEB_SIZE_MB} MB"
echo "  SHA-256      : ${DEB_SHA256}"
echo "  Target Count : Strictly ${FINAL_COUNT} file in '${TARGET_DIR}'"
echo "========================================================================"
echo ""
echo "  To install this package on Debian / Ubuntu / Kali / Mint:"
echo -e "    ${CYAN}sudo dpkg -i \"${FINAL_DEB}\"${RESET}"
echo -e "    ${CYAN}sudo apt-get install -f${RESET}  # (resolves any missing system dependencies)"
echo ""
echo "  To run AquaPulse after installation:"
echo -e "    ${CYAN}aquapulse [video.mp4]${RESET}"
echo ""
echo "  To uninstall:"
echo -e "    ${CYAN}sudo dpkg -r ${PKG_NAME}${RESET}"
echo -e "${GREEN}========================================================================${RESET}"
