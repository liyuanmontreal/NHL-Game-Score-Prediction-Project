"""
download_seasons.py
CLI to download NHL seasons (2016-17 → 2025-26).
"""
import argparse
from src.data.nhl_api_client import NHLDataClient

SEASONS = [
    "20162017",
    "20172018",
    "20182019",
    "20192020",
    "20202021",
    "20212022",
    "20222023",
    "20232024",
    "20242025",
    "20252026",
  
]

def main():
    parser = argparse.ArgumentParser(description="Download NHL seasons play-by-play JSONs")
    parser = argparse.ArgumentParser(description="Download NHL seasons play-by-play JSONs")
    parser.add_argument("--include-types", nargs="*", default=["02","03"], 
                        help="Game types (01=Pre,02=Reg,03=PO)")
    parser.add_argument("--max-games", type=int, default=None, 
                        help="Limit number of downloads per season")
    parser.add_argument("--from-season", type=str, default=SEASONS[0], 
                        help="Start season (e.g., 2016)")
    parser.add_argument("--to-season", type=str, default=SEASONS[-1], 
                        help="End season (e.g., 2023)")
    parser.add_argument("--rate-limit", type=float, default=0.25, 
                        help="Sleep seconds between requests")
    args = parser.parse_args()

    client = NHLDataClient(rate_limit_s=args.rate_limit)
    try:
        start = SEASONS.index(args.from_season)  
    except ValueError:
        start = 0
    try:
        end = SEASONS.index(args.to_season)     
    except ValueError:
        end = len(SEASONS)-1    

    for season in SEASONS[start:end+1]:
        print(f"=== Downloading season {season} (types={args.include_types}) ===")
        client.fetch_season(season, include_types=tuple(args.include_types), max_games=args.max_games)


if __name__ == "__main__":
    main()


