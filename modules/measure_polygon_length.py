import numpy as np


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


# -------------------------------------------
# MEASURE CANINE LENGTH FROM POLYGON
# -------------------------------------------
def measure_polygon_length(points, image_width, image_height, mm_per_pixel):
    # Convert normalized YOLO coords → pixel coords
    px = np.array([p[0] * image_width for p in points])  # Array of x coordinates (in pixels)
    py = np.array([p[1] * image_height for p in points]) # Array of y coordinates (in pixels)

    # Highest & lowest points vertically (the y axis is reversed in pictures).
    # Use the center of the extreme edge to reduce bbox/flat-edge bias.
    eps = 1.0  # pixels
    x1, y1 = _extreme_center(px, py, want_max=False, eps=eps)
    x2, y2 = _extreme_center(px, py, want_max=True, eps=eps)

    pixel_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2) # Apply Pytagoras formula to get the real distance between the two points

    mm_length = pixel_length * mm_per_pixel # Calculate the length based on the reference

    # Return length
    return float(mm_length) 
