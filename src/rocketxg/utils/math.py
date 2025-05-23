import numpy as np
import rlgym.rocket_league.math as rlmath

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

def rectangle_sdf(pos, halfsize) -> float:
    halfsize = np.array(halfsize)
    edge_distance = np.abs(pos) - halfsize
    return np.sum(rlmath.magnitude(np.maximum(edge_distance, 0)))


def distance_to_goal(pos, team) -> float:
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