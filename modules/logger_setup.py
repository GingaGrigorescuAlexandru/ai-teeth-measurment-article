import logging
import os
import sys

# Ensure console supports UTF-8 (fixes emoji errors on Windows)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    # Older Python versions
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# -------------------------------------------
# CONFIGURE LOGGER
# -------------------------------------------
logger = logging.getLogger("tooth_logger")
logger.setLevel(logging.DEBUG)

# Log format
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# -------- Console Handler (UTF-8 safe) --------
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# -------- File Handler (UTF-8 safe) --------
file_handler = logging.FileHandler("logs/app.log", mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Only add handlers once
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
