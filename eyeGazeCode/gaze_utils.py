# gaze_utils.py
"""
If confused about any of these functions or their purpose contact LowerBrick (Zain).
Separate from main eye gaze code for simplicity. But these are essentially helper functions that classify right left center etc.
"""    

from datetime import datetime
import config


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def shape_to_points(shape, indices: list) -> list:
    return [(shape.part(i).x, shape.part(i).y) for i in indices]


def centroid(points: list) -> tuple:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def compute_iris_ratio(outer_x: int, inner_x: int, iris_x: float):
    eye_width = inner_x - outer_x
    if abs(eye_width) < 1:
        return None
    return (iris_x - outer_x) / eye_width


def classify_gaze(iris_ratio: float) -> str:
    if iris_ratio < config.GAZE_LEFT_THRESHOLD:
        return "LEFT"
    elif iris_ratio > config.GAZE_RIGHT_THRESHOLD:
        return "RIGHT"
    else:
        return "CENTER"


def print_gaze(direction: str, ratio: float) -> None:
    print(f"[{timestamp()}]  Gaze: {direction:<6}  (ratio={ratio:.3f})")