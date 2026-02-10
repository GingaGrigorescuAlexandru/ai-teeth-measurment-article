# -------------------------------------------
# LOAD YOLO POLYGONS
# -------------------------------------------
from modules.logger_setup import logger


def _bbox_to_polygon(nums):
    x, y, w, h = nums
    x0 = x - (w / 2.0)
    x1 = x + (w / 2.0)
    y0 = y - (h / 2.0)
    y1 = y + (h / 2.0)
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def load_yolo_polygons(label_path):
    teeth = {"13": [], "23": [], "33": [], "43": []}
    class_map = {"0": "13", "1": "23", "2": "33", "3": "43"}

    with open(label_path, "r") as f:
        for line_no, line in enumerate(f, 1):
            parts = line.strip().split()  # Splits a row of the label file into its corresponding parts
            if not parts:
                continue
            cls = parts[0]                # Gets the class as the first element in the row

            if cls not in class_map:
                continue # Skips the tooth if the class is NOT the one we need

            tooth = class_map[cls]                                         # Gets the tooth number form the map
            nums = list(map(float, parts[1:]))                             # Transforms the strings into float numbers (mask coordinates)

            if len(nums) == 4:
                # YOLO bbox format (x_center, y_center, w, h) detected.
                pts = _bbox_to_polygon(nums)
                logger.warning(
                    "Label %s line %d for class %s looks like a bbox; converted to polygon.",
                    label_path,
                    line_no,
                    cls,
                )
            elif len(nums) < 6 or (len(nums) % 2 != 0):
                logger.warning(
                    "Label %s line %d for class %s has invalid polygon length (%d numbers); skipping.",
                    label_path,
                    line_no,
                    cls,
                    len(nums),
                )
                continue
            else:
                pts = [(nums[i], nums[i+1]) for i in range(0, len(nums), 2)]   # Pairs each consecutive two numbers into point coordinates (YOLO format)

            # Keep the most detailed polygon if multiple appear for the same tooth.
            if teeth[tooth] and len(pts) <= len(teeth[tooth]):
                continue
            teeth[tooth] = pts      # Appends the coordinate points for each mask to the corresponding tooth

    return teeth
