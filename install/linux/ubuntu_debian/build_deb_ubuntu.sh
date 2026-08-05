#!/bin/bash
# AquaPulse Vision Telemetry - Ubuntu/Debian (.deb) Installer Package Builder

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_SRC_DIR="$SCRIPT_DIR/../../../3 - AI process/Vision transfromers"
DEB_ROOT="$SCRIPT_DIR/aquapulse-vision_1.0.0_amd64"

echo "============================================================"
echo "📦 AquaPulse Ubuntu/Debian (.deb) Package Builder"
echo "============================================================"

# Create Debian package structure
mkdir -p "$DEB_ROOT/DEBIAN"
mkdir -p "$DEB_ROOT/usr/bin"
mkdir -p "$DEB_ROOT/usr/share/aquapulse"
mkdir -p "$DEB_ROOT/usr/share/applications"

# Write Control File
cat <<EOF > "$DEB_ROOT/DEBIAN/control"
Package: aquapulse-vision
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: AquaPulse Team <support@aquapulse.ai>
Description: AquaPulse Vision Telemetry - AI Marine Object Tracking & Ollama Persona Suite
 Real-time underwater species tracking, cyberpunk HUD, and local Ollama LLM integration.
EOF

# Write post-install script to ensure Ollama is installed
cat <<'EOF' > "$DEB_ROOT/DEBIAN/postinst"
#!/bin/bash
echo "Installing Ollama AI engine if missing..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
fi
echo "Pulling llama3 AI model..."
ollama pull llama3
EOF
chmod +x "$DEB_ROOT/DEBIAN/postinst"

# Copy App Source to Share Folder
cp -r "$APP_SRC_DIR/"* "$DEB_ROOT/usr/share/aquapulse/"

# Create Executable Launcher
cat <<'EOF' > "$DEB_ROOT/usr/bin/aquapulse-vision"
#!/bin/bash
python3 /usr/share/aquapulse/main.py "$@"
EOF
chmod +x "$DEB_ROOT/usr/bin/aquapulse-vision"

# Create Desktop Launcher Shortcut
cat <<EOF > "$DEB_ROOT/usr/share/applications/aquapulse-vision.desktop"
[Desktop Entry]
Name=AquaPulse Vision Telemetry
Comment=AI Marine Object Tracking & Ollama Telemetry Suite
Exec=/usr/bin/aquapulse-vision %u
Terminal=false
Type=Application
Categories=Science;ArtificialIntelligence;Utility;
EOF

# Build Debian Package
dpkg-deb --build "$DEB_ROOT" "$SCRIPT_DIR/aquapulse-vision_1.0.0_amd64.deb"

echo "============================================================"
echo "🎉 Ubuntu/Debian Package (.deb) Created Successfully!"
echo "Package File: $SCRIPT_DIR/aquapulse-vision_1.0.0_amd64.deb"
echo "Install with: sudo dpkg -i aquapulse-vision_1.0.0_amd64.deb"
echo "============================================================"
