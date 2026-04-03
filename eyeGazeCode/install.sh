#!/bin/bash

# install.sh — Eye Gaze Detector setup script
# Platform: Raspberry Pi 5 / Raspberry Pi OS (Debian-based)

set -e

echo "=== Eye Gaze Detector — Dependency Installer ==="
echo ""

# --- apt packages ---

APT_PACKAGES=(
    python3-picamera2
    python3-opencv
    python3-pip
    python3-numpy
)

echo "Updating package list..."
sudo apt update -qq

for pkg in "${APT_PACKAGES[@]}"; do
    if dpkg -s "$pkg" &>/dev/null; then
        echo "[already installed] $pkg"
    else
        echo "[installing] $pkg"
        sudo apt install -y "$pkg"
    fi
done

echo ""

# --- verify imports ---

echo "Verifying Python imports..."

IMPORTS=(cv2 numpy picamera2)
ALL_OK=true

for mod in "${IMPORTS[@]}"; do
    if python3 -c "import $mod" &>/dev/null; then
        echo "[ok] $mod"
    else
        echo "[FAILED] $mod — could not import"
        ALL_OK=false
    fi
done

echo ""

if $ALL_OK; then
    echo "=== All dependencies installed and verified. ==="
else
    echo "=== Some imports failed. Review errors above. ==="
    exit 1
fi
