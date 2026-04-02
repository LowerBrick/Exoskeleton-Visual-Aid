# config.py
 
# --- Camera resolution (IMX296 native) ---
CAPTURE_WIDTH  = 1456
CAPTURE_HEIGHT = 1088
 
# --- Processing resolution ---
PROCESS_WIDTH  = 640
PROCESS_HEIGHT = 480
 
# --- Frame rate cap ---
FPS_LIMIT = 30
 
# --- Gaze thresholds ---
GAZE_LEFT_THRESHOLD  = 0.40
GAZE_RIGHT_THRESHOLD = 0.60
 
# --- Smoothing ---
SMOOTHING_FRAMES = 5
 
# --- Output behaviour ---
PRINT_ON_CHANGE_ONLY = True
 
# --- Eye detection settings ---
MIN_EYE_SIZE   = 60
IRIS_THRESHOLD = 50
MIN_IRIS_AREA  = 100
 