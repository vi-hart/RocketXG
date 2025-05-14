import numpy as np
import pandas as pd
import RocketSim as rsim
import rlgym.rocket_league.math as rlmath

from rlgym.rocket_league.sim import RocketSimEngine
from .hit_analysis import distance_to_goal

sim = RocketSimEngine()
sim.close()


def detect_shot(pos, team, threshold=500):
    dist = distance_to_goal(pos, not team)
    if dist < threshold:
        return True
    return False


def sim_detect_shot(ball_data, arena, time_s=1):
    is_shot = False
    team = ball_data["hit_team_num"]
    if team:
        goal_dir = 1
    else:
        goal_dir = -1

    tick_rate = round(arena.tick_rate)
    ticks = round(tick_rate*time_s)

    ball_pos = ball_data[["pos_x", "pos_y", "pos_z"]].to_numpy()
    ball_vel = ball_data[["vel_x", "vel_y", "vel_z"]].to_numpy()
    ball_ang_vel = ball_data[["ang_vel_x",
                              "ang_vel_y", "ang_vel_z"]].to_numpy()
    ball_quat = ball_data[["quat_w", "quat_x", "quat_y", "quat_z"]].to_numpy()
    ball_state = rsim.BallState()
    ball_state.pos = rsim.Vec(*ball_pos)
    ball_state.vel = rsim.Vec(*ball_vel)
    ball_state.ang_vel = rsim.Vec(*ball_ang_vel)
    try:
        ball_state.rot_mat = rsim.RotMat(
            *rlmath.quat_to_rot_mtx(ball_quat).transpose().flatten())
    except ValueError:
        pass
    arena.ball.set_state(ball_state)
    ball_sim_data = []
    for _ in range(ticks):
        arena.step(1)
        next_state = arena.ball.get_state()

        is_shot = detect_shot(next_state.pos, team)
        current_ball_state = {"shot": is_shot}
        current_ball_state.update({
            key: val for key, val in zip(["pos_x", "pos_y", "pos_z"], next_state.pos)
        })
        current_ball_state.update({
            key: val for key, val in zip(["vel_x", "vel_y", "vel_z"], next_state.vel)
        })
        current_ball_state.update({
            key: val for key, val in zip(["ang_vel_x", "ang_vel_y", "ang_vel_z"], next_state.ang_vel)
        })
        ball_sim_data.append(current_ball_state)

        # Stop the simulation if hit is going away from net
        if goal_dir*next_state.vel[1] > 0:
            break

        # Stop the simulation if hit is detected as a shot
        if is_shot:
            break
    return is_shot, pd.DataFrame(ball_sim_data)
