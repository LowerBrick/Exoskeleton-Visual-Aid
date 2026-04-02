# Eye Gaze Detector

Real-time eye gaze direction detector for Raspberry Pi 5. A camera is fixed close to one eye and detects whether the subject is looking **LEFT**, **CENTER**, or **RIGHT**. Output is printed to the terminal with a live preview window.

---

## Hardware

| | |
|---|---|
| Device | Raspberry Pi 5 |
| OS | Raspberry Pi OS Trixie (Debian 13) |
| Camera | IMX296 global shutter sensor |
| Resolution | 1456 x 1088 @ 60.38 fps |
| Interface | CSI-2 |

**Physical setup:** Camera mounted 2–5cm from one eye so the eye fills most of the frame.

---

## Dependencies

```bash
sudo apt install python3-picamera2
sudo apt install python3-opencv
sudo apt install python3-pip
pip install dlib --break-system-packages
```

> `dlib` compiles from source on ARM64 — allow ~10 minutes.  
> `numpy` is installed automatically with OpenCV.

---

## Installation

```bash
git clone https://github.com/your-username/eye_gaze.git
cd eye_gaze

wget https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_eye.xml
```

---

## Files

```
eye_gaze/
    eye_gaze_detector.py    Main program — run this
    config.py               All tunable settings
    gaze_utils.py           Helper functions
    haarcascade_eye.xml     OpenCV eye detector model
```

---

## Usage

```bash
python3 eye_gaze_detector.py
```

Press `Q` to quit.

---

## How It Works

Each frame goes through the following pipeline:

1. Capture frame from IMX296 at 1456×1088
2. Resize to 640×480 for faster processing
3. Convert to grayscale — eliminates IR tint from the camera
4. Apply CLAHE contrast enhancement — sharpens iris/sclera boundary
5. Haar cascade scans frame for an eye bounding box
6. Crop to the eye region (ROI)
7. Gaussian blur to reduce eyelash/reflection noise
8. Binary threshold — dark pixels (iris) become white, bright (sclera) black
9. Find contours — largest dark contour = iris
10. Image moments compute the iris centroid
11. `iris_ratio = iris_centre_x / eye_box_width`
    - `0.0` = iris at left edge → gaze **LEFT**
    - `0.5` = iris centred → gaze **CENTER**
    - `1.0` = iris at right edge → gaze **RIGHT**
12. Smooth over last 5 frames (rolling average)
13. Classify and print to terminal

**Preview window overlays:**
- Green rectangle — detected eye bounding box
- Yellow line — vertical centre reference
- Red circle — estimated iris centre
- Coloured text — gaze direction + ratio (Blue=LEFT, Green=CENTER, Orange=RIGHT)
- Threshold inset — b/w iris mask for tuning

---

## Configuration

All settings are in `config.py`:

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

**Camera not in final position** — Testing has been done hand-held. Reliability will improve once the camera is fixed in its final mount.

**Uneven lighting** — A bright overhead light can interfere with detection. A dedicated IR illuminator ring is the standard solution used in professional eye trackers.

---

## Planned Improvements

Replace the Haar cascade + threshold approach with **Hough Circle Transform** (`cv2.HoughCircles`). Since the camera is fixed, the iris always appears in roughly the same region of the frame and is always approximately the same size — which is exactly what HoughCircles is designed for. This removes the need for thresholding entirely and should be significantly more robust to lighting changes and corneal reflections.
