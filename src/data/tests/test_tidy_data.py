"""
src/data/tests/test_tidy_data.py
---------------------------------------
Unit tests for tidy_data module.
使用 pytest 测试 tidy_data 功能。
pytest -q src/data/tests/test_tidy_data.py
"""

import pandas as pd
import sys, os
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if ROOT not in sys.path:
    sys.path.append(ROOT)


from src.data.tidy_data import load_json, tidy_shots_from_game, tidy_all_games


def test_load_json(tmp_path):
    """测试 JSON 加载功能"""
    # Create temporary JSON
    path = tmp_path / "test.json"
    data = {"id": 123, "plays": []}
    path.write_text('{"id": 123, "plays": []}', encoding="utf-8")

    result = load_json(str(path))
    assert result["id"] == 123


def test_tidy_shots_from_game_structure():
  

    """检查输出 DataFrame 结构是否正确"""
    fake_game = {
        "id": 999999,
        "plays": [          
        {
            "eventId": 15,
            "periodDescriptor": {
                "number": 1,
                "periodType": "REG",
                "maxRegulationPeriods": 3
            },
            "timeInPeriod": "02:14",
            "timeRemaining": "17:46",
            "situationCode": "1551",
            "typeCode": 505,
            "typeDescKey": "goal",
            "sortOrder": 33,
            "details": {
                "xCoord": -81,
                "yCoord": 8,
                "zoneCode": "O",
                "shotType": "snap",
                "scoringPlayerId": 8477015,
                "scoringPlayerTotal": 1,
                "assist1PlayerId": 8471436,
                "assist1PlayerTotal": 1,
                "assist2PlayerId": 8475180,
                "assist2PlayerTotal": 1,
                "eventOwnerTeamId": 10,
                "goalieInNetId": 8471418,
                "awayScore": 0,
                "homeScore": 1
            }
            },
            {
            "eventId": 53,
            "periodDescriptor": {
                "number": 1,
                "periodType": "REG",
                "maxRegulationPeriods": 3
            },
            "timeInPeriod": "00:40",
            "timeRemaining": "19:20",
            "situationCode": "1551",
            "typeCode": 506,
            "typeDescKey": "shot-on-goal",
            "sortOrder": 9,
            "details": {
                "xCoord": -38,
                "yCoord": 34,
                "zoneCode": "O",
                "shotType": "snap",
                "shootingPlayerId": 8474157,
                "goalieInNetId": 8475215,
                "eventOwnerTeamId": 8,
                "awaySOG": 1,
                "homeSOG": 0
            }
            },
        ]
  
    }

    df = tidy_shots_from_game(fake_game)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2  # only 2 valid events
    required_cols = [
        "game_id", "event_type", "period", "time_in_period",
        "team_id", "shooter_id", "goalie_id", "shot_type",
        "x", "y", "strength", "empty_net", "is_goal"
    ]
    for col in required_cols:
        assert col in df.columns


def test_tidy_all_games_empty(tmp_path):
    """测试空目录时不报错"""
    empty_dir = tmp_path / "raw"
    empty_dir.mkdir()
    df = tidy_all_games(str(empty_dir))
    assert df.empty
