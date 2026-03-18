#!/bin/bash

# ============================================================
# Visual Aid Exoskeleton - Dependency Installer
# For use on Raspberry Pi 5 only
# ============================================================

set -e  # Exit immediately if any command fails

echo "============================================================"
echo " Visual Aid Exoskeleton - Setup Script"
echo "============================================================"
echo ""

# Step 1: Update the system
echo "[1/5] Updating system packages..."
sudo apt update && sudo apt full-upgrade -y
echo "✓ System updated"
echo ""

# Step 2: Install the IMX500 AI camera package
# This also installs the model files to /usr/share/imx500-models/
echo "[2/5] Installing IMX500 AI camera package..."
sudo apt install -y imx500-all
echo "✓ IMX500 AI camera package installed"
echo ""

# Step 3: Install OpenCV and munkres for object detection
echo "[3/5] Installing OpenCV and munkres..."
sudo apt install -y python3-opencv python3-munkres
echo "✓ OpenCV and munkres installed"
echo ""

# Step 4: Install picamera2
echo "[4/5] Installing picamera2..."
sudo apt install -y python3-picamera2
echo "✓ picamera2 installed"
echo ""

# Step 5: Install espeak-ng for text-to-speech
echo "[5/5] Installing espeak-ng (text-to-speech)..."
sudo apt install -y espeak-ng
echo "✓ espeak-ng installed"
echo ""

echo "============================================================"
echo " All dependencies installed successfully!"
echo ""
echo " To run the visual aid:"
echo "   python3 src/detection.py"
echo ""
echo " Optional flags:"
echo "   --threshold 0.55     Detection confidence threshold"
echo "   --iou 0.65           IOU threshold"
echo "   --max-detections 10  Max objects to detect per frame"
echo "   --fps <n>            Frames per second"
echo "============================================================"
