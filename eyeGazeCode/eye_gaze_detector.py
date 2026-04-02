#!/usr/bin/env python3
# eye_gaze_detector.py
 
import sys
import time
import collections
from pathlib import Path
 
import cv2
import numpy as np
from picamera2 import Picamera2
 
import config
import gaze_utils
 
#Classification model path
CASCADE_PATH = Path(__file__).parent / "haarcascade_eye.xml"
 
 
#Convert to gray scale (just easier for model to detect that way)
def preprocess(frame_rgb):
    gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    return clahe.apply(gray)
 
 #Sliding window with weak classification to detect general eye area
def detect_eye(gray_eq, cascade):
    eyes = cascade.detectMultiScale(
        gray_eq,
        scaleFactor  = 1.1,
        minNeighbors = 5,
        minSize      = (config.MIN_EYE_SIZE, config.MIN_EYE_SIZE),
    )
    if len(eyes) == 0:
        return None
    return max(eyes, key=lambda e: e[2] * e[3])
 
 #More precise detection of iris within actual eye, returns pixel location of center of iris
def find_iris(eye_roi_gray):
    blurred = cv2.GaussianBlur(eye_roi_gray, (7, 7), 0)
    _, thresh = cv2.threshold(
        blurred,
        config.IRIS_THRESHOLD,
        255,
        cv2.THRESH_BINARY_INV,
    )
    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    if not contours:
        return None, None, thresh
    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) < config.MIN_IRIS_AREA:
        return None, None, thresh
    M = cv2.moments(largest)
    if M["m00"] == 0:
        return None, None, thresh
    cx = M["m10"] / M["m00"]
    cy = M["m01"] / M["m00"]
    return cx, cy, thresh
 
#overlays (helps debug when using monitor + pi)
def draw_overlay(frame_bgr, ex, ey, ew, eh, iris_fx, iris_fy, direction, ratio, thresh):
    cv2.rectangle(frame_bgr, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
    centre_x = ex + ew // 2
    cv2.line(frame_bgr, (centre_x, ey), (centre_x, ey + eh), (0, 255, 255), 1)
    cv2.circle(frame_bgr, (iris_fx, iris_fy), 6, (0, 0, 255), 2)
    colour = {
        "LEFT":   (255, 100, 0),
        "CENTER": (0, 220, 0),
        "RIGHT":  (0, 100, 255),
    }.get(direction, (255, 255, 255))
    cv2.putText(
        frame_bgr,
        f"Gaze: {direction}  ratio={ratio:.3f}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0, colour, 2, cv2.LINE_AA,
    )
    try:
        thumb = cv2.resize(thresh, (ew, eh))
        thumb_bgr = cv2.cvtColor(thumb, cv2.COLOR_GRAY2BGR)
        x_start = ex + ew + 10
        x_end   = x_start + ew
        if x_end < frame_bgr.shape[1]:
            frame_bgr[ey:ey + eh, x_start:x_end] = thumb_bgr
            cv2.putText(frame_bgr, "iris mask", (x_start, ey - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    except Exception:
        pass
 
#Starts up and initializes camera
def init_camera():
    cam = Picamera2()
    cam_config = cam.create_video_configuration(
        main={"format": "RGB888", "size": (config.CAPTURE_WIDTH, config.CAPTURE_HEIGHT)},
        display=None,
    )
    cam.configure(cam_config)
    cam.start()
    time.sleep(2.0)
    print(f"[{gaze_utils.timestamp()}]  Camera ready "
          f"({config.CAPTURE_WIDTH}x{config.CAPTURE_HEIGHT})")
    return cam
 

def main():
    if not CASCADE_PATH.exists():
        sys.exit(
            f"[ERROR] Cascade file not found: {CASCADE_PATH}\n"
            "Run: wget https://raw.githubusercontent.com/opencv/opencv/"
            "master/data/haarcascades/haarcascade_eye.xml"
        )
    cascade = cv2.CascadeClassifier(str(CASCADE_PATH))
    if cascade.empty():
        sys.exit("[ERROR] Cascade file loaded but is empty — file may be corrupted. "
                 "Re-download it.")
    print(f"[{gaze_utils.timestamp()}]  Haar cascade loaded.")
 
    cam = init_camera()
 
    ratio_buffer   = collections.deque(maxlen=config.SMOOTHING_FRAMES)
    last_direction = ""
    frame_count    = 0
    start_time     = time.time()
    min_interval   = (1.0 / config.FPS_LIMIT) if config.FPS_LIMIT else 0.0
    last_frame_t   = 0.0
 
    print(f"[{gaze_utils.timestamp()}]  Running. Press Q to quit.\n")
 
    while True:
        now = time.time()
        gap = now - last_frame_t
        if gap < min_interval:
            time.sleep(min_interval - gap)
        last_frame_t = time.time()
 
        frame_rgb = cam.capture_array("main")
        frame_count += 1
 
        frame_small = cv2.resize(
            frame_rgb,
            (config.PROCESS_WIDTH, config.PROCESS_HEIGHT),
            interpolation=cv2.INTER_LINEAR,
        )
 
        gray_eq   = preprocess(frame_small)
        frame_bgr = cv2.cvtColor(frame_small, cv2.COLOR_RGB2BGR)
        eye       = detect_eye(gray_eq, cascade)
 
        if eye is None:
            ratio_buffer.clear()
            last_direction = ""
            cv2.putText(frame_bgr, "No eye detected", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.imshow("Eye Gaze", frame_bgr)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            continue
 
        ex, ey, ew, eh = eye
        eye_roi = gray_eq[ey:ey + eh, ex:ex + ew]
        iris_cx, iris_cy, thresh = find_iris(eye_roi)
 
        if iris_cx is None:
            cv2.rectangle(frame_bgr, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
            cv2.putText(frame_bgr, "Iris not found — adjust IRIS_THRESHOLD",
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 165, 255), 2, cv2.LINE_AA)
            cv2.imshow("Eye Gaze", frame_bgr)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            continue
 
        ratio = iris_cx / ew
        ratio_buffer.append(ratio)
        smoothed  = sum(ratio_buffer) / len(ratio_buffer)
        direction = gaze_utils.classify_gaze(smoothed)
 
        iris_frame_x = int(ex + iris_cx)
        iris_frame_y = int(ey + iris_cy)
        draw_overlay(frame_bgr, ex, ey, ew, eh,
                     iris_frame_x, iris_frame_y,
                     direction, smoothed, thresh)
 
        cv2.imshow("Eye Gaze", frame_bgr)
 
        if config.PRINT_ON_CHANGE_ONLY:
            if direction != last_direction:
                gaze_utils.print_gaze(direction, smoothed)
                last_direction = direction
        else:
            gaze_utils.print_gaze(direction, smoothed)
 
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
 
    elapsed = time.time() - start_time
    avg_fps = frame_count / elapsed if elapsed > 0 else 0
    print(f"\n[{gaze_utils.timestamp()}]  Stopped. "
          f"{frame_count} frames in {elapsed:.1f}s ({avg_fps:.1f} fps avg).")
    cam.stop()
    cv2.destroyAllWindows()
 
 
if __name__ == "__main__":
    main()