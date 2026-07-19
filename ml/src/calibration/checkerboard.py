import cv2
import numpy as np


def detect_checkerboard_corners(
    grayscale: np.ndarray,
    checkerboard: tuple[int, int],
    max_detection_dimension: int = 1280,
) -> np.ndarray | None:
    """Detect quickly on a scaled image, then return points in original pixel coordinates."""
    height, width = grayscale.shape[:2]
    scale = min(1.0, max_detection_dimension / max(height, width))
    detection_image = grayscale
    if scale < 1.0:
        detection_image = cv2.resize(
            grayscale,
            (round(width * scale), round(height * scale)),
            interpolation=cv2.INTER_AREA,
        )
    found, corners = cv2.findChessboardCorners(
        detection_image,
        checkerboard,
        flags=cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE,
    )
    if not found:
        return None
    corners = corners.astype(np.float32) / scale
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.01)
    return cv2.cornerSubPix(grayscale, corners, (7, 7), (-1, -1), criteria)
