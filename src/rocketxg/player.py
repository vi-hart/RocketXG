import numpy as np
import RocketSim as rsim
from statistics import mode
from rlgym_tools.rocket_league.replays.parsed_replay import ParsedReplay
from typing import List
from .shot_detection import sim_detect_shot

class Player:
    def __init__(self, name: str, id: int, is_orange: bool):
        self.name = name
        self.id = id
        self.is_orange = is_orange
        self.all_hits = []
        self.isolated_hits = []
        self.dribbles = []
        self.followups = []
        self.shots = {}
    
    def generate_possessions(self, dribble_threshold=15):
        if not self.all_hits:
            return
        
        possession = None
        possessions = []
        for hit in self.all_hits:
            if hit.player_changed:
                if possession:
                    if len(possession) == 1:
                        self.isolated_hits.append(possession[0])
                    else:
                        frames = [hit.frame for hit in possession]
                        delta_frames = np.diff(frames)
                        if mode(delta_frames) < dribble_threshold:
                            self.dribbles.append(possession)
                        else:
                            self.followups.append(possession)
                        0
                possession = [hit]
                possessions.append(possession)
            else:
                possession.append(hit)
    
    def generate_shots(self, replay: ParsedReplay, time_s=1):
        arena = rsim.Arena(rsim.GameMode.SOCCAR)
        for hit in self.isolated_hits:
            ball_data = replay.ball_df.iloc[hit.frame, :]
            is_shot, sim_data = sim_detect_shot(ball_data, arena, time_s)
            hit.is_shot = is_shot
            if is_shot:
                self.shots[hit] = {
                    "ball_state": ball_data,
                    "sim_data": sim_data
                }
            
        for dribble in self.possessions:
            hit = dribble[-1]
            ball_data = replay.ball_df.iloc[hit.frame, :]
            is_shot, sim_data = sim_detect_shot(ball_data, arena, time_s)
            hit.is_shot = is_shot
            if is_shot:
                self.shots[hit] = {
                    "ball_state": ball_data,
                    "sim_data": sim_data
                }
        arena.stop()
        
    
    @property
    def possessions(self):
        return self.dribbles + self.followups
    
    
def generate_players(replay: ParsedReplay):
    for player in replay.metadata["players"]:
        if isinstance(player["is_orange"], bool):
            yield Player(
                name = player["name"],
                id = player["unique_id"],
                is_orange = player["is_orange"]
            )