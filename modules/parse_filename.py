import os
import re

# -------------------------------------------
# PARSE AGE + TITLE + SEX FROM FILE NAME
# -------------------------------------------
def parse_filename(filename):
    base = os.path.basename(filename) # Get the file name from the path

    # Title = everything before ".rf"
    title = base.split(".rf")[0]

    # Age: preferred match for both -39-ani and -39-de-ani
    match = re.search(r"-([0-9]{1,3})-(?:de-)?ani", base)
    if match:
        age = int(match.group(1))
    else:
        # Fallback: if there are at least two numbers in the title, treat the last as age
        numbers = re.findall(r"\d{1,3}", title)
        age = int(numbers[-1]) if len(numbers) >= 2 else None

    # Sex: matches -B-/-F- as well as -B or _B before extension
    sex_match = re.search(r"(?:^|[-_])(B|F)(?:[-_.]|$)", title, re.IGNORECASE)
    sex = sex_match.group(1).upper() if sex_match else None
    return title, age, sex
