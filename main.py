"""
main.py
Unified entry point .
"""

from src.utils.config import print_config
from src.data.nhl_api_client import NHLDataClient
from src.features.feature_engineering import build_features
from src.models.baseline_models import train_logistic_regression
from src.models.evaluation import evaluate_model
from src.serving.flask_app import start_server

def main():
    print("=== NHL Game Score Prediction Project  ===")
    print_config()

    # 1. Data acquisition
    client = NHLDataClient()
    raw_data = client.fetch_season("2023-24")

    # 2. Feature engineering
    df = build_features(raw_data)

    # 3. Model training and evaluation
    model = train_logistic_regression(df)
    evaluate_model(model, df)

    # 4. Serve model (optional)
    start_server()

if __name__ == "__main__":
    main()
