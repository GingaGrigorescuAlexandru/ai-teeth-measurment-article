import numpy as np


# GET PEAKS FUNCTION 
def get_peak_point(points, image_width, image_height, t):
    '''Returns the 2D point representing the peak of the tooth'''
    # Convert normalized YOLO coords → pixel coords
    px = np.array([p[0] * image_width for p in points])  # Array of x coordinates (in pixels)
    py = np.array([p[1] * image_height for p in points]) # Array of y coordinates (in pixels)

    if t in ["13", "23"]: # If maxilar canine get the bottom most point
        peak_idx = np.argmax(py)
    else:
        peak_idx = np.argmin(py) # If mandibular canine get the top most point

    peak_x, peak_y = px[peak_idx], py[peak_idx] # Get the peak point in pixels


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
    
