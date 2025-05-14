import sys
from rlgym_tools.rocket_league.replays.parsed_replay import ParsedReplay
import rocketxg as rxg
import pandas as pd
from rocketxg.hit_analysis import get_shooter_analysis, get_opponent_analysis, get_ball_analysis

def run(replay_dir: str):
    replay = ParsedReplay.load(replay_dir)
    hits = rxg.generate_hits_table(replay)
    players = list(hits.keys())
    dataset = []
    for player in players:
        player.generate_possessions()
        player.generate_shots(replay, time_s=3)
        for shot, data in player.shots.items():
            game_state = {}
            ball_data = get_ball_analysis(shot, replay)
            game_state.update(ball_data)
            opponent_data = get_opponent_analysis(shot, players, replay)
            game_state.update(opponent_data)
            shooter_data = get_shooter_analysis(shot, replay)
            game_state.update(shooter_data)
            dataset.append(game_state)
    
    dataset_df = pd.DataFrame(dataset)
    dataset_df.to_parquet(replay_dir.removesuffix(".replay") + ".parquet")
            
            
            
            
    
if __name__ == "__main__":
    replay_dir = sys.argv[1]
    run(replay_dir)