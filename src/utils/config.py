"""
config.py
Global configuration constants for NHL data project.
"""

import os

# API base URL
API_BASE_URL = "https://api-web.nhle.com/v1/gamecenter"

# Data directories
DATA_DIR = "./data"
RAW_DIR = os.path.join(DATA_DIR, "raw")

# Ensure directories exist
os.makedirs(RAW_DIR, exist_ok=True)


def print_config():
    print(f"[INFO] API base URL: {API_BASE_URL}")
    print(f"[INFO] Data directory: {DATA_DIR}")
    print(f"[INFO] Raw data directory: {RAW_DIR}")
