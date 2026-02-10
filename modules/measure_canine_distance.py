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


# GET PEAKS FUNCTION 
def get_peak_point(points, image_width, image_height, t):
    '''Returns the 2D point representing the peak of the tooth'''
    # Convert normalized YOLO coords → pixel coords
    px = np.array([p[0] * image_width for p in points])  # Array of x coordinates (in pixels)
    py = np.array([p[1] * image_height for p in points]) # Array of y coordinates (in pixels)

    eps = 1.0  # pixels
    if t in ["13", "23"]: # If maxilar canine get the bottom most point
        peak_x, peak_y = _extreme_center(px, py, want_max=True, eps=eps)
    else:
        peak_x, peak_y = _extreme_center(px, py, want_max=False, eps=eps) # If mandibular canine get the top most point

    return (float(peak_x), float(peak_y))   # convert here too

# -------------------------------------------
# MEASURE CANINE DISTANCE
# -------------------------------------------
def measure_canine_distance(peaks, mm_per_pixel):
    # Apply Pytagoras formula to get the real distance between the two points
    if peaks["13"] is not None and peaks["23"] is not None: # Check if both points exist
        pixel_distance_13_23 = np.sqrt((peaks["13"][0] - peaks["23"][0])**2 + (peaks["13"][1] - peaks["23"][1])**2) 
        distance_13_23 = pixel_distance_13_23 * mm_per_pixel
    else:
        distance_13_23 = None

    if peaks["33"] is not None and peaks["43"] is not None: # Check if both points exist
        pixel_distance_33_43 = np.sqrt((peaks["33"][0] - peaks["43"][0])**2 + (peaks["33"][1] - peaks["43"][1])**2) 
        distance_33_43 = pixel_distance_33_43 * mm_per_pixel
    else:
        distance_33_43 = None


    return (
        float(distance_13_23) if distance_13_23 is not None else None,
        float(distance_33_43) if distance_33_43 is not None else None
    )
    
