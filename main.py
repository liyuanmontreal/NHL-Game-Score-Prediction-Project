"""
main.py
Step 1.1: Test NHL API data downloading.
"""

from src.utils.config import print_config
from src.data.nhl_api_client import NHLDataClient
from src.features.feature_engineering import build_features
from src.models.baseline_models import train_logistic_regression
from src.models.evaluation import evaluate_model
from src.serving.flask_app import start_server
from src.data.tidy_data import summarize_game_info


def main():
    print("=== Step 1.1: NHL Data Download Test ===")
    print_config()

    # 1. Data acquisition
    # Create client   
    client = NHLDataClient()
    #raw_data = client.fetch_season("2023-24")

    # Example game ID (2022–23 playoffs)
    game_id = "2022030411"
    raw_data = client.fetch_game(game_id)

    if raw_data:
        print(f"[SUCCESS] Game {game_id} downloaded successfully!")
        #print(f"[INFO] Keys in JSON: {list(raw_data.keys())[:10]}")
        summarize_game_info(raw_data)
    else:
        print(f"[FAIL] Could not download game {game_id}")

    
    # 2. Feature engineering
    df = build_features(raw_data)

    # 3. Model training and evaluation
    model = train_logistic_regression(df)
    evaluate_model(model, df)

    # 4. Serve model (optional)
    start_server()


if __name__ == "__main__":
    main()



