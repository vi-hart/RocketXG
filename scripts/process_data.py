import os
import sys
import uuid
from pathlib import Path
from rlgym_tools.rocket_league.replays.parsed_replay import ParsedReplay
import rocketxg as rxg
import pandas as pd
from rocketxg.hit_analysis import get_shooter_analysis, get_opponent_analysis, get_ball_analysis

def run(replay_dir: str, out_dir: str):
    for path in Path(replay_dir).rglob('*.replay'):
        if path.is_dir():
            continue
        print(f"Path: {path}")
        os.makedirs(out_dir, exist_ok=True)
        out_path = Path(out_dir) / "data.parquet"
        replay = ParsedReplay.load(path)
        hits = rxg.generate_hits_table(replay)
        players = list(hits.keys())
        game_id = uuid.uuid4()
        dataset = []
        for player in players:
            player.generate_possessions()
            player.generate_shots(replay, time_s=3)
            for shot, data in player.shots.items():
                game_state = {
                    "game_id": game_id.hex,
                    "is_goal": shot.is_goal
                }
                ball_data = get_ball_analysis(shot, replay)
                game_state.update(ball_data)
                opponent_data = get_opponent_analysis(shot, players, replay)
                game_state.update(opponent_data)
                shooter_data = get_shooter_analysis(shot, replay)
                game_state.update(shooter_data)
                dataset.append(game_state)
        
        dataset_df = pd.DataFrame(dataset)
        try:
            if out_path.exists():
                dataset_df.to_parquet(out_path, engine='fastparquet', append=True)
            else:
                dataset_df.to_parquet(out_path, engine='fastparquet')
        except Exception as e:
            Warning(e)
            
            
            
            
    
if __name__ == "__main__":
    replay_dir = sys.argv[1]
    out_dir = sys.argv[2]
    run(replay_dir, out_dir)