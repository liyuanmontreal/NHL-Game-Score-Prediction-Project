"""
Normalize NHL shot coordinates so that all shots are in the offensive zone (+x).
"""
import os, json, pandas as pd
from typing import Dict

def build_defending_side_index(raw_dir: str) -> Dict[str, Dict[int, str]]:
    """Return {game_id: {period: 'left'|'right'}} using homeTeamDefendingSide."""
    idx = {}
    for fn in os.listdir(raw_dir):
        if not fn.startswith("game_") or not fn.endswith(".json"):
            continue
        with open(os.path.join(raw_dir, fn), "r", encoding="utf-8") as f:
            g = json.load(f)
        gid = str(g.get("id"))
        per_map = {}
        for p in g.get("plays", []):
            pdsc = p.get("periodDescriptor", {}) or {}
            num = pdsc.get("number")
            side = pdsc.get("homeTeamDefendingSide")
            if num and side and num not in per_map:
                per_map[num] = side
        if not per_map:
            per_map = {1: "left", 2: "right", 3: "left", 4: "right", 5: "left"}
        idx[gid] = per_map
    return idx

def normalize_to_offense(df: pd.DataFrame, raw_dir: str) -> pd.DataFrame:
    """
    Add x_off, y_off where all shots are in offensive (+x) direction.
    """
    idx = build_defending_side_index(raw_dir)
    home_away = {}
    for fn in os.listdir(raw_dir):
        if fn.startswith("game_") and fn.endswith(".json"):
            with open(os.path.join(raw_dir, fn), "r", encoding="utf-8") as f:
                g = json.load(f)
            home_away[str(g.get("id"))] = (
                g.get("homeTeam", {}).get("id"),
                g.get("awayTeam", {}).get("id"),
            )

    df = df.copy()
    xo, yo = [], []
    for _, r in df.iterrows():
        gid = str(r["game_id"])
        period = int(r.get("period", 1))
        x, y, team = r["x"], r["y"], r["team_id"]
        home_def = idx.get(gid, {}).get(period, "left")
        home_id, away_id = home_away.get(gid, (None, None))
        offense_right = (home_def == "left") if team == home_id else (home_def == "right")
        if offense_right:
            xo.append(abs(x)); yo.append(y)
        else:
            xo.append(-abs(x)); yo.append(-y)
    df["x_off"], df["y_off"] = xo, yo
    return df[(df["x_off"] >= 0) & df["x_off"].notna() & df["y_off"].notna()]
