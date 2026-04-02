# Visual Aid Exoskeleton

A wearable computer vision system built on the Raspberry Pi 5. It detects objects in real time and announces them aloud using text-to-speech, and tracks eye gaze direction to detect whether the user is looking LEFT, CENTER, or RIGHT — designed as an assistive visual aid.

---

## Hardware Requirements

| Component | Details |
|---|---|
| Device | Raspberry Pi 5 |
| OS | Raspberry Pi OS Trixie (Debian 13) |
| Object Detection Camera | Raspberry Pi AI Camera (IMX500) |
| Eye Gaze Camera | IMX296 global shutter sensor |
| Power | USB-C PD 5V/5A power supply |
| Storage | SanDisk Extreme microSD (or equivalent) |

> **Note:** The IMX500 AI camera is required for on-device object detection inference and cannot be substituted. The IMX296 must be mounted 2–5cm from one eye so the eye fills most of the frame.

---

## Project Structure

```
visual-aid-exoskeleton/
├── README.md
├── install.sh
├── requirements.txt
├── src/
│   └── detection.py
├── assets/
│   └── coco_labels.txt
├── eye_gaze/
│   ├── eye_gaze_detector.py
│   ├── config.py
│   ├── gaze_utils.py
│   └── haarcascade_eye.xml
```

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/LowerBrick/Visual-Aid-Exoskeleton.git
cd visual-aid-exoskeleton
```

### 2. Run the installer
```bash
chmod +x install.sh
./install.sh
```

This installs all required system packages. The `imx500-all` step may take a few minutes as it downloads camera firmware and model files.

### 3. Install eye gaze dependencies
```bash
sudo apt install python3-picamera2
sudo apt install python3-opencv
sudo apt install python3-pip
pip install dlib --break-system-packages
```

> `dlib` compiles from source on ARM64 — allow ~10 minutes.

### 4. Download the Haar cascade model
```bash
cd eye_gaze
wget https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_eye.xml
```

---

## Usage

### Object Detection
```bash
python3 src/detection.py
```

| Flag | Default | Description |
|---|---|---|
| `--threshold` | `0.55` | Minimum confidence to register a detection |
| `--iou` | `0.65` | IOU threshold for overlapping boxes |
| `--max-detections` | `10` | Max objects detected per frame |
| `--fps` | auto | Frames per second |
| `--labels` | COCO-80 | Path to a custom labels file |

### Eye Gaze Detection
```bash
python3 eye_gaze/eye_gaze_detector.py
```

Press `Q` to quit.

---

## How It Works

### Object Detection

The IMX500 camera handles image sensing and on-chip AI inference, sending an output tensor to the Pi 5. The Pi parses that tensor to extract detected objects, draws bounding boxes on the preview, and announces detected object names aloud via `espeak-ng`. Detection uses the COCO-80 dataset, which covers 80 common everyday objects.

### Eye Gaze Detection

Each frame goes through the following pipeline:

1. Capture frame from IMX296 at 1456×1088
2. Resize to 640×480 for faster processing
3. Convert to grayscale — eliminates IR tint from the camera
4. Apply CLAHE contrast enhancement — sharpens iris/sclera boundary
5. Haar cascade scans frame for an eye bounding box
6. Gaussian blur to reduce eyelash/reflection noise
7. Binary threshold — dark pixels (iris) become white, bright (sclera) black
8. Find contours — largest dark contour = iris
9. Image moments compute the iris centroid
10. `iris_ratio = iris_centre_x / eye_box_width`
    - `0.0` = iris at left edge → gaze **LEFT**
    - `0.5` = iris centred → gaze **CENTER**
    - `1.0` = iris at right edge → gaze **RIGHT**
11. Smooth over last 5 frames and classify

**Preview window overlays:**
- Green rectangle — detected eye bounding box
- Yellow line — vertical centre reference
- Red circle — estimated iris centre
- Coloured text — gaze direction + ratio (Blue=LEFT, Green=CENTER, Orange=RIGHT)
- Threshold inset — b/w iris mask for tuning

---

## Eye Gaze Configuration

All settings are in `eye_gaze/config.py`:

| Setting | Default | Description |
|---|---|---|
| `CAPTURE_WIDTH / HEIGHT` | 1456, 1088 | IMX296 native resolution |
| `PROCESS_WIDTH / HEIGHT` | 640, 480 | Resolution used for detection |
| `FPS_LIMIT` | 30 | Max frames processed per second |
| `GAZE_LEFT_THRESHOLD` | 0.40 | iris_ratio below this → LEFT |
| `GAZE_RIGHT_THRESHOLD` | 0.60 | iris_ratio above this → RIGHT |
| `SMOOTHING_FRAMES` | 5 | Frames to average before classifying |
| `PRINT_ON_CHANGE_ONLY` | True | Only print when direction changes |
| `MIN_EYE_SIZE` | 60 | Minimum eye detection size in pixels |
| `IRIS_THRESHOLD` | 50 | Dark pixel cutoff for iris isolation (0–255) |
| `MIN_IRIS_AREA` | 100 | Minimum contour area to count as iris |

---

## Known Issues

**Iris detection unreliable** — The Haar cascade + threshold approach is sensitive to lighting changes. Corneal reflections break the iris contour and confuse the centroid calculation.

**Eye gaze camera not in final position** — Testing has been done hand-held. Reliability will improve once the camera is fixed in its final mount.

**Uneven lighting** — A bright overhead light can interfere with gaze detection. A dedicated IR illuminator ring is the standard solution used in professional eye trackers.

---

## Planned Features

- Replace Haar cascade + threshold with Hough Circle Transform (`cv2.HoughCircles`) for more reliable iris detection
- Custom trained dataset for broader object detection beyond COCO-80
- Servo control driven by eye gaze direction (left/right)
- Additional object detection running directly on the Pi 5 as a fallback

---

## Dependencies

See `requirements.txt` for the full list. System dependencies are installed via `install.sh`.
