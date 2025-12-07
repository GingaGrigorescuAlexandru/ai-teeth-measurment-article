# -------------------------------------------
# LOAD YOLO POLYGONS
# -------------------------------------------
def load_yolo_polygons(label_path):
    teeth = {"13": [], "23": [], "33": [], "43": []}
    class_map = {"0": "13", "1": "23", "2": "33", "3": "43"}

    with open(label_path, "r") as f:
        for line in f:
            parts = line.strip().split()  # Splits a row of the label file into its corresponding parts
            cls = parts[0]                # Gets the class as the first element in the row

            if cls not in class_map:
                continue # Skips the tooth if the class is NOT the one we need

            tooth = class_map[cls]                                         # Gets the tooth number form the map
            nums = list(map(float, parts[1:]))                             # Transforms the strings into float numbers (mask coordinates)
            pts = [(nums[i], nums[i+1]) for i in range(0, len(nums), 2)]   # Pairs each consecutive two numbers into point coordinates (YOLO format)

            teeth[tooth] = pts      # Appends the coordinate points for each mask to the corresponding tooth

    return teeth