# Visual Aid Exoskeleton

A wearable computer vision system built on the Raspberry Pi 5 and Raspberry Pi AI Camera (IMX500). It detects objects in real time and announces them aloud using text-to-speech — designed as an assistive visual aid.

---

## Hardware Requirements

- Raspberry Pi 5
- Raspberry Pi AI Camera (IMX500)
- USB-C PD 5V/5A power supply
- SanDisk Extreme microSD card (or equivalent)

> **Note:** This project will not run on any other hardware. The IMX500 AI camera is required for on-device inference.

---

## How It Works

The IMX500 camera module handles image sensing and on-chip AI inference, sending an output tensor to the Pi 5. The Pi then parses that tensor to extract detected objects, draws bounding boxes on the preview, and speaks detected object names aloud via `espeak-ng`.

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/visual-aid-exoskeleton.git
cd visual-aid-exoskeleton
```

### 2. Run the installer
```bash
chmod +x install.sh
./install.sh
```

This installs all required system packages. The `imx500-all` step may take a few minutes as it downloads camera firmware and model files.

---

## Running

```bash
python3 src/detection.py
```

### Optional flags

| Flag | Default | Description |
|------|---------|-------------|
| `--threshold` | `0.55` | Minimum confidence to register a detection |
| `--iou` | `0.65` | IOU threshold for overlapping boxes |
| `--max-detections` | `10` | Max objects detected per frame |
| `--fps` | auto | Frames per second |
| `--labels` | COCO-80 | Path to a custom labels file |

---

## Object Detection Model

By default the system uses the COCO-80 dataset, which covers 80 common everyday objects. This is the only publicly available dataset in the `.rpk` format required by the IMX500 chip.

Custom dataset training is in progress to expand detection coverage.

---

## Project Structure

```
visual-aid-exoskeleton/
├── README.md
├── install.sh
├── requirements.txt
├── src/
│   └── detection.py
└── assets/
    └── coco_labels.txt
```

---

## Planned Features

- Custom trained dataset for broader object detection
- Eye tracking via second camera input and servo control (left/right)
- Additional object detection running directly on the Pi 5 as a fallback

---

## Dependencies

See `requirements.txt` for the full list. All dependencies are installed via `apt` through `install.sh`.
