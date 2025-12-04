# -------------------------------------------
# LOAD YOLO POLYGONS
# -------------------------------------------
def load_yolo_polygons(label_path):
    teeth = {"13": [], "23": [], "33": [], "43": []}
    class_map = {"0": "13", "1": "23", "2": "33", "3": "43"}

    with open(label_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            cls = parts[0]

            if cls not in class_map:
                continue

            tooth = class_map[cls]
            nums = list(map(float, parts[1:]))
            pts = [(nums[i], nums[i+1]) for i in range(0, len(nums), 2)]

            teeth[tooth].append(pts)

    return teeth