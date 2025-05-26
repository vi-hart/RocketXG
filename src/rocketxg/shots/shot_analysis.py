import pandas as pd
import numpy as np
import rlgym.rocket_league.math as rlmath
from dataclasses import asdict
from typing import List
from rlgym.rocket_league.common_values import (
    ORANGE_GOAL_CENTER,
    BLUE_GOAL_CENTER,
    GOAL_CENTER_TO_POST
)
from ..possessions.base import Hit

class ShotAnalyzer:
    def __init__(self, shots: List[Hit]):
        self.shots = shots
        self.data: pd.DataFrame = None
        
    def analyze(self):
        full_stats = []
        for shot in self.shots:
            if shot.hit_type != "shot":
                continue
            shot_stats = asdict(shot)
            ###-- Ball --###
            team = shot.team
            op_team = not team
            ball_pos = shot.get_ball_pos()
            # Distance from Net
            dist = distance_to_goal_center(ball_pos, op_team)
            angle = goal_angle(ball_pos, op_team)
            # Height
            # Speed
            # Net Angle
            shot_stats.update({
                "ball_distance": dist,
                "goal_angle": angle,
                "ball_height": ball_pos[2]
            })
            ###-- Shooter --###
            # Boost at possession start
            # Boost at shot
            # Speed
            ###-- Teammates --###
            ###-- Opponents --###
            full_stats.append(shot_stats)
        self.data = pd.DataFrame(full_stats)
        return self.data
        
    

def distance_to_goal_center(pos: tuple, team: bool):
    goal_pos = ORANGE_GOAL_CENTER if team else BLUE_GOAL_CENTER
    return rlmath.euclidean_distance(np.array(pos), np.array(goal_pos))

def goal_angle(pos: tuple, team: bool):
    assert len(pos) > 1, "Position must have at least 2 coordinates (x, y)"
    if team:
        x, y = ORANGE_GOAL_CENTER[0] - pos[0], ORANGE_GOAL_CENTER[1] - pos[1]
    else:
        x, y = pos[0] - BLUE_GOAL_CENTER[0], pos[1] - BLUE_GOAL_CENTER[1]
        
    w = GOAL_CENTER_TO_POST
    theta = np.arctan(
        2*w*y / (x**2 + y**2 - w**2)
    )
    if theta < 0:
        return theta + np.pi
    return theta
    
    