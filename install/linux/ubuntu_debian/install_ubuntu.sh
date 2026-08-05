#!/bin/bash
# AquaPulse 1-Click Installer for Ubuntu / Debian Linux

set -e

echo "============================================================"
echo "⚡ AquaPulse Vision Telemetry 1-Click Installer (Ubuntu/Debian)"
echo "============================================================"

# Check and install Ollama
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama AI Engine..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

echo "🧠 Verifying Llama3 AI Model..."
ollama pull llama3

# Install Python requirements
echo "📦 Installing PyTorch & Vision Dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-tk python3-opencv
pip3 install ultralytics opencv-python torch torchvision langchain-ollama pyttsx3 requests

echo "============================================================"
echo "🎉 AquaPulse Setup Complete!"
echo "Run application using: python3 main.py"
echo "============================================================"
