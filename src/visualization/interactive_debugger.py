
"""
Interactive Debugger v3 — DataFrame + Better Labels
NHL 比赛事件交互调试工具 v3 — 使用 DataFrame 展示 + 更友好的名称映射
--------------------------------------------------------------------
- ipywidgets: Dropdown for Game, Event type; Dropdown for Period with "All"
- Matplotlib: scatter points over rink background (auto-download if missing)
- pandas: tabular display of selected events (player/team names, jersey numbers)
"""
import os
import json
import requests
from io import BytesIO
from typing import Dict, Any, List, Optional

import matplotlib.pyplot as plt
from PIL import Image
from ipywidgets import interact, Dropdown, Output
from IPython.display import display
import pandas as pd

# =============================
#  Path Handling / 路径处理
# =============================
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
RAW_DIR = os.path.join(ROOT_DIR, "data", "raw")
RINK_IMG_PATH = os.path.join(ROOT_DIR, "src", "visualization", "rink_image.png")

# ===================================
#  Auto-download Rink / 自动下载冰场图
# ===================================
def ensure_rink_image():
    if not os.path.exists(RINK_IMG_PATH):
        print("[INFO] Downloading rink image... / 正在下载冰场背景图...")
        url = "https://upload.wikimedia.org/wikipedia/commons/3/3a/Ice_hockey_rink_diagram.svg"
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            img = Image.open(BytesIO(r.content)).convert("RGBA")
            os.makedirs(os.path.dirname(RINK_IMG_PATH), exist_ok=True)
            img.save(RINK_IMG_PATH)
            print(f"[INFO] Saved to {RINK_IMG_PATH}")
        except Exception as e:
            print(f"[WARN] Failed to download rink image: {e} / 下载失败，可忽略将不显示底图。")

# =====================================
#  Load & Extract / 加载与提取
# =====================================
def load_game_data(game_id: str) -> Optional[Dict[str, Any]]:
    path = os.path.join(RAW_DIR, f"game_{game_id}.json")
    if not os.path.exists(path):
        print(f"[WARN] Missing file: {path}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_team_map(game: Dict[str, Any]) -> Dict[int, Dict[str, str]]:
    team_map: Dict[int, Dict[str, str]] = {}
    for side in ("homeTeam", "awayTeam"):
        t = game.get(side, {}) or {}
        tid = t.get("id")
        if tid is None:
            continue
        team_map[tid] = {
            "abbrev": t.get("abbrev", "UNK"),
            "name": (t.get("commonName", {}) or {}).get("default", "Unknown Team"),
        }
    return team_map

def build_player_map(game: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    """Return {playerId: {'name': 'First Last', 'number': 'xx'}}"""
    pmap: Dict[int, Dict[str, Any]] = {}
    for spot in game.get("rosterSpots", []) or []:
        pid = spot.get("playerId")
        if not pid:
            continue
        first = (spot.get("firstName", {}) or {}).get("default", "") or ""
        last = (spot.get("lastName", {}) or {}).get("default", "") or ""
        jersey = spot.get("jerseyNumber") or ""
        pmap[pid] = {"name": (f"{first} {last}").strip() or f"Player {pid}", "number": str(jersey) if jersey else ""}
    return pmap

def extract_events(game: Dict[str, Any]) -> List[Dict[str, Any]]:
    plays = game.get("plays", []) or []
    events: List[Dict[str, Any]] = []
    for p in plays:
        details = p.get("details", {}) or {}
        # Coordinates may be missing
        if "xCoord" in details and "yCoord" in details:
            # Try to resolve best-effort player id key
            #  球员ID提取逻辑
            player_id = (
                details.get("scoringPlayerId")
                or details.get("shootingPlayerId")
                or details.get("hittingPlayerId")
                or details.get("committedByPlayerId")
                or details.get("winningPlayerId")               
                or details.get("fightingPlayerId1")
                or details.get("playerId")
        
         
            )

            events.append(
                {
                    "type": p.get("typeDescKey", "unknown"),
                    "period": (p.get("periodDescriptor", {}) or {}).get("number", "?"),
                    "time": p.get("timeInPeriod", "?"),
                    "teamId": details.get("eventOwnerTeamId"),
                    "playerId": player_id,
                    "x": details.get("xCoord"),
                    "y": details.get("yCoord"),
                    "homeScore": details.get("homeScore"),
                    "awayScore": details.get("awayScore"),
                }
            )
    return events

# =====================================
#  Plot & Table / 绘图与表格
# =====================================
def plot_and_table(game_id: str, event_type: Optional[str] = "All", period: Optional[str] = "All", max_rows: int = 15):
    ensure_rink_image()
    game = load_game_data(game_id)
    if not game:
        return

    team_map = build_team_map(game)
    player_map = build_player_map(game)
    events = extract_events(game)

    # Filter by type & period
    if event_type not in (None, "", "All"):
        events = [e for e in events if e["type"] == event_type]
    if period not in (None, "", "All"):
        events = [e for e in events if str(e["period"]) == str(period)]

    # --- Build DataFrame ---
    rows = []
    for e in events:
        tinfo = team_map.get(e.get("teamId"), {"abbrev": f"ID{e.get('teamId')}", "name": "Unknown Team"})
        pinfo = player_map.get(e.get("playerId"), {"name": f"ID{e.get('playerId')}", "number": ""})
        rows.append(
            {
                "eventType": e["type"],
                "period": e["period"],
                "time": e["time"],
                "teamAbbrev": tinfo["abbrev"],
                "teamName": tinfo["name"],
                "teamId": e.get("teamId"),
                "playerName": pinfo["name"],
                "jersey": pinfo["number"],
                "playerId": e.get("playerId"),
                "x": e["x"],
                "y": e["y"],
                #"score": f"{e.get('homeScore', '')}-{e.get('awayScore', '')}",
            }
        )
    df = pd.DataFrame(rows, columns=[
        "eventType", "period", "time",
        "teamAbbrev", "teamName", "teamId",
        "playerName",  "playerId",
        "x", "y"
    ])

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(10, 6))
    if os.path.exists(RINK_IMG_PATH):
        rink = Image.open(RINK_IMG_PATH)
        ax.imshow(rink, extent=[-100, 100, -42.5, 42.5])
    else:
        ax.set_facecolor("#EAF6FF")
    ax.set_title(f"Game {game_id} — {event_type or 'All'} | Period: {period or 'All'}  "
                 f"({len(df)} events)")

    if not df.empty:
        ax.scatter(df["x"], df["y"], s=40, alpha=0.75)
    else:
        ax.text(0, 0, "No events found / 未找到事件", ha="center", va="center", fontsize=14)
    ax.set_xlim(-100, 100); ax.set_ylim(-42.5, 42.5)
    plt.xlabel("X"); plt.ylabel("Y")
    plt.show()

    # --- Table ---
    if df.empty:
        print("No events to display")
    else:
        display(df.head(max_rows))

# =====================================
#  Interactive UI / 交互界面
# =====================================
def interactive_debugger(season: Optional[str] = None, all_games: bool = False):
    """
    Launch interactive debugger.
    season: e.g., "20222023"; if None and all_games=False, auto-choose first season found.
    all_games: if True, load all game files under data/raw.
    """
    if not os.path.exists(RAW_DIR):
        print(f"[ERROR] Missing directory: {RAW_DIR}")
        return
    files = [f for f in os.listdir(RAW_DIR) if f.startswith("game_") and f.endswith(".json")]
    if not files:
        print("[ERROR] No JSON files found in data/raw")
        return

    # Build game list
    if all_games:
        game_ids = [f.split("game_")[1].split(".json")[0] for f in files]
    else:      
        game_ids = [f.split("game_")[1].split(".json")[0] for f in files if "game_"+season[:4] in f]

    if not game_ids:
        print(f"[WARN] No games found for season={season}")
        return

    event_types = ["All", "goal", "shot-on-goal", "missed-shot", "blocked-shot", "penalty"]
    periods = ["All", 1, 2, 3, 4, 5]

    out = Output()

    def _update(game_id, event_type, period):
        with out:
            out.clear_output(wait=True)
            plot_and_table(game_id, event_type, period)

    interact(
        _update,
        game_id=Dropdown(options=sorted(game_ids), description="Game 比赛:"),
        event_type=Dropdown(options=event_types, value="All", description="Event 事件:"),
        period=Dropdown(options=periods, value="All", description="Period 节:")
    )
    display(out)
