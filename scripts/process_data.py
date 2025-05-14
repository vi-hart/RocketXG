import os
import sys
from pathlib import Path
from rlgym_tools.rocket_league.replays.parsed_replay import ParsedReplay
import rocketxg as rxg
import pandas as pd
from rocketxg.hit_analysis import get_shooter_analysis, get_opponent_analysis, get_ball_analysis

def run(replay_dir: str):
    for path in Path(replay_dir).rglob('*.replay'):
        out_path = Path("data/test.parquet")
        os.makedirs(out_path.parent, exist_ok=True)
        replay = ParsedReplay.load(path)
        hits = rxg.generate_hits_table(replay)
        players = list(hits.keys())
        dataset = []
        for player in players:
            player.generate_possessions()
            player.generate_shots(replay, time_s=3)
            for shot, data in player.shots.items():
                game_state = {"is_goal": shot.is_goal}
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
    run(replay_dir)