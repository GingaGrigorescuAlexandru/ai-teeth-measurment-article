import os
import re

# -------------------------------------------
# PARSE AGE + TITLE FROM FILE NAME
# -------------------------------------------
def parse_filename(filename):
    base = os.path.basename(filename) # Get the file name from the path

    # Title = everything before ".rf"
    title = base.split(".rf")[0]

    # Age: matches both -39-ani and -39-de-ani
    match = re.search(r"-([0-9]{1,3})-(?:de-)?ani", base)
    if not match:
        raise ValueError(f"❌ Could not extract age from filename: {base}")

    age = int(match.group(1)) # Get the age as it's the first group in the 
    return title, age