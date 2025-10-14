"""
nhl_api_client.py

Use API download NHL play-by-play JSON files for full seasons.
- Combines stable ID enumeration from original project
- Keeps retry, rate limit, caching, and improved logging
- Adjusts season ranges and prints success statistics
"""

import os, time, requests, json
from typing import Optional, List, Set, Tuple
from src.utils.config import API_BASE_URL, RAW_DIR

DEFAULT_TIMEOUT = 20
RETRY_STATUS = {429, 500, 502, 503, 504}

class NHLDataClient:
    def __init__(self, rate_limit_s: float = 0.25):
        self.base = API_BASE_URL.rstrip('/')
        self.rate_limit_s = rate_limit_s
        self.session = requests.Session()

    def play_by_play_url(self, game_id: str) -> str:
        return f"{self.base}/gamecenter/{game_id}/play-by-play"

    def schedule_url(self, season: str) -> str:
        #TODO：this port doesn't work now
        return f"{self.base}/schedule/season/{season}"

    def _request_json(self, url: str, max_retries: int = 3) -> Optional[dict]:
        backoff = 0.5
        for attempt in range(1, max_retries + 1):
            try:
                r = self.session.get(url, timeout=DEFAULT_TIMEOUT)
                if r.status_code == 200:
                    return r.json()
                if r.status_code in RETRY_STATUS:
                    print(f"[INFO] Retry {attempt}/{max_retries} after status {r.status_code}...")
                    time.sleep(backoff); backoff *= 2
                    continue
                return None
            except requests.RequestException as e:
                print(f"[WARN] Network error: {e} (attempt {attempt})")
                time.sleep(backoff); backoff *= 2
        return None

    def discover_game_ids_via_schedule(self, season: str) -> List[str]:        
        url = self.schedule_url(season)     
        data = self._request_json(url)
        ids = set()  # Using set to avoid duplicates

        if not data:
            return [] # Return empty if no data
        def visit(node):
            if isinstance(node, dict): 
                 # Check for ID fields in dictionary keys
                for k in ('id','gameId','gamePk'): 
                    v = node.get(k)
                    if isinstance(v, (int,str)):
                        s = str(v)
                        if len(s)==10 and s.isdigit():
                            ids.add(s)
                # Recursively visit all dictionary values
                for v in node.values(): visit(v)
            elif isinstance(node, list):
                for v in node: visit(v)
        visit(data)
        #print (ids)
        return sorted(ids)

    def guess_game_ids_fallback(self, season: str, include_types=('02','03')) -> List[str]:
        season = str(season)
        ids = []
        reg_cap = 1300 if int(season[:4]) < 2020 else 1275
        po_cap = 400
        for t in include_types:
            if t == '02':
                for n in range(1, reg_cap + 1):
                    ids.append(f"{season[:4]}{t}{n:04d}")
            elif t == '03':
                for n in range(1, po_cap + 1):
                    ids.append(f"{season[:4]}{t}{n:04d}")
        #print(ids)
        return ids

    def discover_game_ids(self, season: str, include_types=('02','03')) -> List[str]:
        # TODO: currently get id by schedule not work
        # ids = self.discover_game_ids_via_schedule(season)      
        # if ids:
        #     print(f"[INFO] Found {len(ids)} game IDs via schedule API for {season}.")
        #     return [gid for gid in ids if gid[8:10] in include_types]
        print(f"[INFO] Schedule API unavailable for {season}, using legacy fallback enumeration...")
        return self.guess_game_ids_fallback(season, include_types)

    def _cache_path(self, gid: str) -> str:
        return os.path.join(RAW_DIR, f"game_{gid}.json")

    def fetch_game(self, gid: str, force: bool=False) -> Optional[dict]:
        path = self._cache_path(gid)
        if not force and os.path.exists(path):
            return None
        url = self.play_by_play_url(gid)
        data = self._request_json(url)
        time.sleep(self.rate_limit_s)
        if not data: return None
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return data

    def fetch_season(self, season: str, include_types=('02','03'), max_games: Optional[int]=None) -> Tuple[int,int]:
        game_ids = self.discover_game_ids(season, include_types)
        total, saved, failures = len(game_ids), 0, 0
        for gid in game_ids:
            if max_games and saved >= max_games: break
            data = self.fetch_game(gid, force=False)
            if data is not None:
                saved += 1
                if saved % 50 == 0:
                    print(f"[INFO] {saved} games saved for {season} so far...")
            else:
                failures += 1
        print(f"[INFO] Season {season}: {saved} new files, {failures} skipped/cached, total IDs {total}.")
        success_rate = (saved / total * 100) if total > 0 else 0
        print(f"[INFO] Success rate: {success_rate:.2f}%\n")
        return saved, failures