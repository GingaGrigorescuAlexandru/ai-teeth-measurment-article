import os
import re

# -------------------------------------------
# PARSE AGE + TITLE FROM FILE NAME
# -------------------------------------------
def parse_filename(filename):
    base = os.path.basename(filename)

    # Title = everything before ".rf"
    if ".rf" in base:
        title = base.split(".rf")[0]
    else:
        title = os.path.splitext(base)[0]

    # Age: matches both -39-ani and -39-de-ani
    match = re.search(r"-([0-9]{1,3})-(?:de-)?ani", base)
    if not match:
        raise ValueError(f"❌ Could not extract age from filename: {base}")

    age = int(match.group(1))
    return title, age