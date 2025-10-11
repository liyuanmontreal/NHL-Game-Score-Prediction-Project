"""
config.py
Global configuration constants.
"""

API_BASE_URL = "https://api-web.nhle.com/v1/gamecenter"
DATA_DIR = "./data"
RANDOM_SEED = 42

def print_config():
    print(f"[INFO] API base URL: {API_BASE_URL}")
    print(f"[INFO] Data directory: {DATA_DIR}")
