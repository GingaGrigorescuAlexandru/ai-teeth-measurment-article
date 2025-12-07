import numpy as np

# -------------------------------------------
# MEASURE CANINE LENGTH FROM POLYGON
# -------------------------------------------
def measure_polygon_length(points, image_width, image_height):
    # Convert normalized YOLO coords → pixel coords
    px = np.array([p[0] * image_width for p in points])  # Array of x coordinates (in pixels)
    py = np.array([p[1] * image_height for p in points]) # Array of y coordinates (in pixels)

    # Highest & lowest indexes of points vertically (the y axis is reversed in pictures)
    top_idx = np.argmin(py)
    bot_idx = np.argmax(py)

    x1, y1 = px[top_idx], py[top_idx] # Store the pair of top x and y coordinates
    x2, y2 = px[bot_idx], py[bot_idx] # Store the pair of bottom x and y coordinates

    pixel_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2) # Apply Pytagoras formula to get the real distance between the two points

    # OPG real physical width = 270 mm
    mm_per_pixel = 270 / image_width

    mm_length = pixel_length * mm_per_pixel # Calculate the length based on the reference

    # Return length
    return mm_length 