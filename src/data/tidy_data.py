"""
tidy_data.py
Converts raw event JSON data into tidy pandas DataFrames.

"""

def tidy_shots(raw_data):
    print("[Placeholder] Transform raw JSON to tidy shot/goal DataFrame")
    return None


def summarize_game_info(game_json):
    """Summarize metadata of one NHL game."""
    ...
"""
main.py
Step 1.1: Test NHL API data downloading and print sample content.
"""

from src.utils.config import print_config
from src.data.nhl_api_client import NHLDataClient

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

