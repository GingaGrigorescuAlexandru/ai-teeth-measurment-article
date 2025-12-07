# Image processing modules
from PIL import Image
import os

# Modules
from modules.logger_setup import logger
from modules.parse_filename import parse_filename
from modules.load_yolo_polygons import load_yolo_polygons
from modules.measure_polygon_length import measure_polygon_length
from modules.measure_canine_distance import get_peak_point, measure_canine_distance
from modules.insert_opg_record import insert_opg_record


# ------------------------------
# PROCESS A SINGLE IMAGE + LABEL
# ------------------------------
def process_opg(image_path, label_path):
    try:
        title, age = parse_filename(image_path)
    except Exception as e:
        logger.error(str(e))
        return

    # Open image to get real resolution
    img = Image.open(image_path)
    image_width, image_height = img.size
    
    # Get the scale of each pixel for the standard image size of 270 mm
    mm_per_pixel = 270 / image_width

    logger.info(f"\n🖼  Processing {title}")
    logger.info(f"   → Resolution: {image_width} × {image_height}")
    logger.info(f"   → Pixel Scale: {mm_per_pixel} mm")

    # Load polygon data
    polygons = load_yolo_polygons(label_path)

    # Measure tooth lengths
    lengths = {}
    peaks = {}
    for t in ["13", "23", "33", "43"]: # Loop through each type of tooth
        if polygons[t]:
            lengths[t] = measure_polygon_length(
                polygons[t], image_width, image_height, mm_per_pixel
            )
            peaks[t] = get_peak_point(
                polygons[t], image_width, image_height, t
            )
        else: # If there is no such tooth, set as None
            lengths[t] = None 
            peaks[t] = None 

    # Call the module function to calculate the canine distances
    distance_13_23, distance_33_43 = measure_canine_distance(peaks, mm_per_pixel)

    # Read raw files
    with open(image_path, "rb") as f:
        img_bytes = f.read() # Read the bytes of the image

    with open(label_path, "r") as f:
        label_txt = f.read() # Read the text of the label

    # UPSERT into database
    insert_opg_record(
        title, age,
        float(lengths["13"]) if lengths["13"] is not None else None,
        float(lengths["23"]) if lengths["23"] is not None else None,
        float(lengths["33"]) if lengths["33"] is not None else None,
        float(lengths["43"]) if lengths["43"] is not None else None,
        float(distance_13_23) if distance_13_23 is not None else None,
        float(distance_33_43) if distance_33_43 is not None else None,
        img_bytes, label_txt,
    )

    logger.info(f"✔ Stored in DB | Age: {age}")



# -------------------------------------------
# PROCESS ALL FILES IN FOLDERS
# -------------------------------------------
def process_all(base_dir):
    img_dir = os.path.join(base_dir, "images")   # Create image folder path
    label_dir = os.path.join(base_dir, "labels") # Create label folder path

    images = sorted([ # Create list of sorted image files
        f for f in os.listdir(img_dir)
        if f.lower().endswith((".jpg", ".png", ".jpeg"))
    ])

    logger.info(f"\n📁 Found {len(images)} OPG images.")
    logger.info("🚀 Starting batch processing...\n")

    for img_file in images:                                 # Loop through each image file
        img_path = os.path.join(img_dir, img_file)          # Get the path of each image
        base = os.path.splitext(img_file)[0]                # Get he name of the file without the extension
        label_path = os.path.join(label_dir, base + ".txt") # Use the base name to get the label path

        if not os.path.exists(label_path):
            logger.warning(f"❌ Missing label for {img_file}, skipping.")
            continue

        process_opg(img_path, label_path)

    logger.info("\n🎉 DONE! All OPG files processed successfully.\n")



# -------------------------------------------
# RUN
# -------------------------------------------
if __name__ == "__main__":
    process_all("datasets\\removed-no-reference\\train")
