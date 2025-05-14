import numpy as np
import pandas as pd
import rlgym.rocket_league.math as rlmath
from typing import List
from rlgym_tools.rocket_league.replays.parsed_replay import ParsedReplay
from rlgym.rocket_league.common_values import (
    BLUE_TEAM,
    ORANGE_TEAM,
    BLUE_GOAL_CENTER,
    ORANGE_GOAL_CENTER,
    GOAL_THRESHOLD,
    GOAL_HEIGHT,
    GOAL_CENTER_TO_POST,
    CEILING_Z
)

def rectangle_sdf(pos, halfsize):
    halfsize = np.array(halfsize)
    edge_distance = np.abs(pos) - halfsize
    return np.sum(rlmath.magnitude(np.maximum(edge_distance, 0)))


def distance_to_goal(pos, team):
    if team:
        goal_pos = ORANGE_GOAL_CENTER
        y_offset = GOAL_THRESHOLD
    else:
        goal_pos = BLUE_GOAL_CENTER
        y_offset = -GOAL_THRESHOLD

    offset = np.array(goal_pos)
    offset[1] += y_offset
    halfsize = [
        GOAL_CENTER_TO_POST,
        GOAL_THRESHOLD,
        GOAL_HEIGHT / 2
    ]

    return rectangle_sdf(pos - offset, halfsize)


def goal_side_sign(is_orange):
    if is_orange:
        return -1
    else:
        return 1

def get_opponent_analysis(hit, players, replay: ParsedReplay):
    player_dfs = replay.player_dfs
    goal_side = goal_side_sign(hit.player.is_orange)
    opponents = {}
    opponent_num = 0
    for player in players:
        if player.is_orange != hit.player.is_orange:
            prefix = f"op_{opponent_num}_"
            player_df = player_dfs[str(player.id)].iloc[hit.frame, :]
            opponent_data = {
                prefix + "pos_x": goal_side*player_df["pos_x"],
                prefix + "pos_y": goal_side*player_df["pos_y"],
                prefix + "pos_z": player_df["pos_z"],
                prefix + "vel_x": goal_side*player_df["vel_x"],
                prefix + "vel_y": goal_side*player_df["vel_y"],
                prefix + "vel_z": player_df["vel_z"],
                prefix + "boost_amount": player_df["boost_amount"]
            }
            opponents.update(opponent_data)
            opponent_num += 1
            
    return opponents

def get_shooter_analysis(hit, replay: ParsedReplay):
    player_df = replay.player_dfs[str(hit.player.id)].iloc[hit.frame, :]
    goal_side = goal_side = goal_side_sign(hit.player.is_orange)
    prefix = "shooter_"
    return {
        prefix + "pos_x": goal_side*player_df["pos_x"],
        prefix + "pos_y": goal_side*player_df["pos_y"],
        prefix + "pos_z": player_df["pos_z"],
        prefix + "vel_x": goal_side*player_df["vel_x"],
        prefix + "vel_y": goal_side*player_df["vel_y"],
        prefix + "vel_z": player_df["vel_z"],
        prefix + "boost_amount": player_df["boost_amount"]
    }
    
def get_ball_analysis(hit, replay: ParsedReplay):
    ball_df = replay.ball_df.iloc[hit.frame, :]
    goal_side = goal_side = goal_side_sign(hit.player.is_orange)
    prefix = "ball_"
    return {
        prefix + "pos_x": goal_side*ball_df["pos_x"],
        prefix + "pos_y": goal_side*ball_df["pos_y"],
        prefix + "pos_z": ball_df["pos_z"],
        prefix + "vel_x": goal_side*ball_df["vel_x"],
        prefix + "vel_y": goal_side*ball_df["vel_y"],
        prefix + "vel_z": ball_df["vel_z"],
    }