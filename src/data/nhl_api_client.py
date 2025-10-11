"""
nhl_api_client.py
Handles NHL API data retrieval and caching.
"""

import os
import requests
from src.utils.config import API_BASE_URL, RAW_DIR
from src.data.data_cache import save_json, load_json


class NHLDataClient:
    def __init__(self, season="20232024"):
        """
        Initialize the data client.
        Args:
            season (str): NHL season identifier, e.g., '20232024'
        """
        self.season = season
        self.base_url = API_BASE_URL
        self.save_dir = RAW_DIR
        os.makedirs(self.save_dir, exist_ok=True)

    def _get_game_url(self, game_id):
        """Construct full API URL for a game."""
        return f"{self.base_url}/{game_id}/play-by-play"

    def fetch_game(self, game_id, force_download=False):
        """
        Download a single game's play-by-play JSON data.
        If cached, load it instead unless force_download=True.
        """
        filepath = os.path.join(self.save_dir, f"game_{game_id}.json")

        if not force_download and os.path.exists(filepath):
            print(f"[INFO] Using cached file for game {game_id}")
            return load_json(filepath)

        url = self._get_game_url(game_id)
        print(f"[INFO] Downloading game {game_id} from {url}")
        resp = requests.get(url)

        if resp.status_code == 200:
            data = resp.json()
            save_json(data, filepath)
            return data
        else:
            print(f"[ERROR] Failed to fetch {game_id}: HTTP {resp.status_code}")
            return None

    def fetch_season(self, game_ids):
        """
        Download multiple games.
        Args:
            game_ids (list[str]): list of game IDs.
        """
        all_data = []
        for gid in game_ids:
            data = self.fetch_game(gid)
            if data:
                all_data.append(data)
        print(f"[INFO] Fetched {len(all_data)} valid games.")
        return all_data
