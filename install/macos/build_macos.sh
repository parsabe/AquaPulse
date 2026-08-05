#!/bin/bash
# AquaPulse Vision Telemetry - macOS Standalone App & DMG Installer Builder

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_SRC_DIR="$SCRIPT_DIR/../../3 - AI process/Vision transfromers"
DIST_DIR="$SCRIPT_DIR/dist"

echo "============================================================"
echo "🍏 AquaPulse Vision macOS App Builder"
echo "============================================================"

# 1. Install dependencies on macOS
pip install --upgrade pip
pip install pyinstaller torch torchvision ultralytics opencv-python pyttsx3 langchain-ollama requests

# 2. Build .app bundle with PyInstaller
echo "🛠️ Compiling AquaPulse Vision into macOS .app bundle..."
pyinstaller --noconfirm --windowed \
    --name="AquaPulse Vision" \
    --add-data="$APP_SRC_DIR/fish_model.pt:." \
    --add-data="$APP_SRC_DIR/main.mp4:." \
    --hidden-import=ultralytics \
    --hidden-import=langchain_ollama \
    --hidden-import=pyttsx3 \
    --distpath="$DIST_DIR" \
    --workpath="$SCRIPT_DIR/work" \
    "$APP_SRC_DIR/main.py"

echo "============================================================"
echo "🎉 macOS App Bundle Created Successfully!"
echo "Location: $DIST_DIR/AquaPulse Vision.app"
echo "============================================================"
