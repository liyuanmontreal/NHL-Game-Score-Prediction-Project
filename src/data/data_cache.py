"""
data_cache.py
Handles saving and loading cached JSON files.
"""

import json
import os


def save_json(data, filepath):
    """Save a Python dict as a JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[INFO] Saved JSON to {filepath}")


def load_json(filepath):
    """Load JSON file if exists."""
    if not os.path.exists(filepath):
        print(f"[WARN] File not found: {filepath}")
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[INFO] Loaded JSON from {filepath}")
    return data
