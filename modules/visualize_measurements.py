import os
import numpy as np

from modules.logger_setup import logger


def _extreme_center(px, py, want_max, eps):
    target = float(np.max(py) if want_max else np.min(py))
    if want_max:
        mask = py >= (target - eps)
    else:
        mask = py <= (target + eps)

    if not np.any(mask):
        idx = int(np.argmax(py) if want_max else np.argmin(py))
        return float(px[idx]), target

    x = float(np.mean(px[mask]))
    return x, target


def _vertical_extremes(points, image_width, image_height):
    """Return pixel coordinates for the top and bottom points of a polygon."""
    px = np.array([p[0] * image_width for p in points])
    py = np.array([p[1] * image_height for p in points])

    eps = 1.0  # pixels
    top_x, top_y = _extreme_center(px, py, want_max=False, eps=eps)
    bot_x, bot_y = _extreme_center(px, py, want_max=True, eps=eps)

    top = (int(round(top_x)), int(round(top_y)))
    bottom = (int(round(bot_x)), int(round(bot_y)))
    return top, bottom


def _round_peak(pt):
    return (int(round(pt[0])), int(round(pt[1])))


def visualize_measurements(image_path, polygons, peaks, output_dir="exports/visualizations"):
    """
    Draw canine length lines (orange) and inter-canine distance lines (red) on the image.
    """
    try:
        import cv2
    except ImportError:
        logger.warning("OpenCV not installed; skipping visualization for %s", image_path)
        return None

    img = cv2.imread(image_path)
    if img is None:
        logger.warning("Could not read image for visualization: %s", image_path)
        return None

    image_height, image_width = img.shape[:2]

    os.makedirs(output_dir, exist_ok=True)

    length_color = (0, 140, 255)  # Orange (BGR)
    distance_color = (0, 0, 255)  # Red (BGR)
    thickness = 2

    # Draw canine length lines
    for tooth, pts in polygons.items():
        if not pts:
            continue
        top, bottom = _vertical_extremes(pts, image_width, image_height)
        img = cv2.line(img, top, bottom, length_color, thickness)

    # Draw inter-canine distance lines
    if peaks.get("13") is not None and peaks.get("23") is not None:
        img = cv2.line(
            img,
            _round_peak(peaks["13"]),
            _round_peak(peaks["23"]),
            distance_color,
            thickness,
        )

    if peaks.get("33") is not None and peaks.get("43") is not None:
        img = cv2.line(
            img,
            _round_peak(peaks["33"]),
            _round_peak(peaks["43"]),
            distance_color,
            thickness,
        )

    output_path = os.path.join(output_dir, os.path.basename(image_path))
    try:
        cv2.imwrite(output_path, img)
        logger.info("Saved visualization to %s", output_path)
    except Exception as exc:
        logger.error("Failed to save visualization for %s: %s", image_path, exc)
        return None

    return output_path
