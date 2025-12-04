import numpy as np

# -------------------------------------------
# MEASURE CANINE LENGTH FROM POLYGON
# -------------------------------------------
def measure_polygon_length(points, image_width, image_height):
    # Convert normalized YOLO coords → pixel coords
    px = np.array([p[0] * image_width for p in points])
    py = np.array([p[1] * image_height for p in points])

    # Highest & lowest points vertically
    top_idx = np.argmin(py)
    bot_idx = np.argmax(py)

    x1, y1 = px[top_idx], py[top_idx]
    x2, y2 = px[bot_idx], py[bot_idx]

    pixel_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    # OPG real physical width = 270 mm
    mm_per_pixel = 270 / image_width

    mm_length = pixel_length * mm_per_pixel

    # Correct for 25% magnification (OPGs enlarge structures 1.25×)
    return mm_length / 1.25