"""
src/data/tidy_data.py
---------------------------------------
Convert NHL raw play-by-play JSON data 
into a tidy pandas DataFrame for analysis.

将 NHL 原始逐场事件 JSON 数据转化为整洁的 Pandas DataFrame。
仅保留 shots 与 goals 事件。
"""

import os
import json
import pandas as pd
from typing import List, Dict
from src.utils.config import print_config
from src.data.nhl_api_client import NHLDataClient

# =============================
#  Path Handling / 路径处理
# =============================
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
RAW_DIR = os.path.join(ROOT_DIR, "data", "raw")


def load_json(filepath: str) -> dict:
    """Load JSON safely 加载JSON文件"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"[ERROR] File not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def tidy_shots_from_game(game_json: dict) -> pd.DataFrame:
    """Convert one game's shots & goals into tidy rows.
    将单场比赛中的shots与goals事件整理为DataFrame行"""

    
    game_id = game_json.get("id")   
    events = game_json.get("plays", [])

    rows = []
    for event in events:
        event_type = event.get("typeDescKey")
        if event_type not in ["shot-on-goal", "goal"]:
            continue  # 忽略其他事件类型

        

        details = event.get("details", {})
        period = event.get("periodDescriptor", {}).get("number")
        period_type = event.get("periodDescriptor", {}).get("periodType")
        time_in_period = event.get("timeInPeriod")
        time_remaining = event.get('timeRemaining', None)
        event_team_id = details.get("eventOwnerTeamId")
        event_id = event.get('eventId', None)

        # 球员与球队映射
        shooter_id = (
            details.get("shootingPlayerId") or
            details.get("scoringPlayerId") or
            details.get("committedByPlayerId")
        )
        goalie_id = details.get("goalieInNetId")

        # 强度与空网
        strength = details.get("strength")
        empty_net = details.get("emptyNet", False)

        # 坐标与射门类型
        x, y = details.get("xCoord"), details.get("yCoord")
        shot_type = details.get("shotType", "Unknown")

        # 过滤无效射门类型
        if not shot_type or str(shot_type).lower() in ["unknown", "none", "na", ""]:
            continue
        
        # Zone Code for figuring out which side the team is on
        zone_code = event.get('details', {}).get('zoneCode', None)

        rows.append({
            "game_id": game_id,
            'event_id': event_id,
            "event_type": event_type,
            "period": period,
            "period_type": period_type,
            "time_in_period": time_in_period,
            'time_remaining': time_remaining,
            "team_id": event_team_id,
            "shooter_id": shooter_id,
            "goalie_id": goalie_id,
            "shot_type": shot_type,
            "x": x,
            "y": y,
            "strength": strength,
            "empty_net": empty_net,
            "is_goal": 1 if event_type == "goal" else 0,
            'zone_code': zone_code
        })         

    return pd.DataFrame(rows)




def tidy_all_games(raw_dir: str =  RAW_DIR, save: bool = True) -> pd.DataFrame:
    """
    Aggregate all games into DataFrames grouped by season and save as CSV.  
    """

    season_dfs = {}

    for file in os.listdir(raw_dir):
        if not file.endswith(".json"):
            continue
        path = os.path.join(raw_dir, file)

        # === 自动识别赛季 ===
        try:
            # 文件名如 "game_20200001.json"
            year_str = file.split("game_")[1][:4]
            start_year = int(year_str)
            end_year = start_year + 1
            season_label = f"{start_year}{end_year}"
        except Exception:
            season_label = "unknown"

        try:
            data = load_json(path)
            df = tidy_shots_from_game(data)
            if not df.empty:
                df["season"] = season_label
                if season_label not in season_dfs:
                    season_dfs[season_label] = []
                season_dfs[season_label].append(df)
        except Exception as e:
            print(f"[WARN] Skipping {file}: {e}")

    if not season_dfs:
        print("[WARN] No valid games processed.")
        return pd.DataFrame()

    # 合并并保存每个赛季
    all_dfs = []
    for season, dfs in season_dfs.items():
        combined = pd.concat(dfs, ignore_index=True)
        all_dfs.append(combined)

        if save:
            processed_dir = os.path.join("data", "processed")
            os.makedirs(processed_dir, exist_ok=True)
            csv_path = os.path.join(processed_dir, f"tidy_shots_{season}.csv")
            combined.to_csv(csv_path, index=False)
            size_mb = os.path.getsize(csv_path) / (1024 * 1024)
            print(f"[INFO] Saved {csv_path} ({size_mb:.2f} MB, {len(combined)} rows)")

    # 生成全赛季合并文件
    full_df = pd.concat(all_dfs, ignore_index=True)
    if save:
        all_path = os.path.join("data", "processed", "tidy_shots_all.csv")
        full_df.to_csv(all_path, index=False)
        size_mb = os.path.getsize(all_path) / (1024 * 1024)
        print(f"[INFO] Saved combined dataset: {all_path} ({size_mb:.2f} MB)")

    return full_df



def summarize_game_info(game_json):
    """Print key stats and first few goal events with player and team names."""
    if not game_json:
        print("[ERROR] No data to summarize.")
        return

    # === Build playerId → playerName mapping ===
    roster_data = (
        game_json.get("rosterSpots")
        or game_json.get("roster")
        or game_json.get("playerList")
        or []
    )
    player_map = {}
    for p in roster_data:
        pid = p.get("playerId")
        if pid:
            first = p.get("firstName", {}).get("default", "")
            last = p.get("lastName", {}).get("default", "")
            name = f"{first} {last}".strip()
            player_map[pid] = name

    # === Build teamId → teamName mapping ===
    home_team = game_json.get("homeTeam", {})
    away_team = game_json.get("awayTeam", {})

    home_id = home_team.get("id", "Unknown")
    away_id = away_team.get("id", "Unknown")

    home_name = home_team.get("commonName", {}).get("default", "Unknown")
    away_name = away_team.get("commonName", {}).get("default", "Unknown")

    team_map = {
        home_id: home_name,
        away_id: away_name,
    }

    # === Metadata ===
    game_date = game_json.get("gameDate", "N/A")
    plays = game_json.get("plays", [])
    total_events = len(plays)
    goals = [p for p in plays if p.get("typeDescKey") == "goal"]
    shots = [p for p in plays if p.get("typeDescKey") == "shot-on-goal"]

    # === Summary Header ===
    print("\n=== Sample Game Summary ===")
    print(f"Date: {game_date}")
    print(f"Teams: {away_name} @ {home_name}")
    print(f"Total Events: {total_events}")
    print(f"Shots on Goal: {len(shots)} | Goals: {len(goals)}")

    if not goals:
        print("[INFO] No goals recorded in this game.")
        print("===========================\n")
        return

    print("\n--- Goal Events (up to 3) ---")

    for i, g in enumerate(goals[:3]):
        details = g.get("details", {})
        scorer_id = details.get("scoringPlayerId")
        assist1_id = details.get("assist1PlayerId")
        assist2_id = details.get("assist2PlayerId")
        team_id = details.get("eventOwnerTeamId")

        scorer_name = player_map.get(scorer_id, f"Unknown (ID {scorer_id})")
        assist1_name = player_map.get(assist1_id, "—")
        assist2_name = player_map.get(assist2_id, "—")
        team_name = team_map.get(team_id, f"Unknown (ID {team_id})")

        print(f"\nGoal #{i+1}")
        print(f"  • eventId: {g.get('eventId', 'N/A')}")
        print(f"  • Team: {team_name}")
        print(f"  • Scored by: {scorer_name}")
        print(f"  • Assist: {assist1_name}, {assist2_name}")
        print(
            f"  • Period: {g.get('periodDescriptor', {}).get('number', '?')}, "
            f"Time: {g.get('timeInPeriod', '?')}"
        )
        print(
            f"  • Coordinates: ({details.get('xCoord')}, {details.get('yCoord')})"
        )
        print(
            f"  • Score: {details.get('awayScore', '?')} - {details.get('homeScore', '?')}"
        )

    print("===========================\n")

    # Optional: Return mappings for external use
    return {"player_map": player_map, "team_map": team_map}

if __name__ == "__main__":
    df = tidy_all_games()
    print(df.head(10))

