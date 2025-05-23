import pandas as pd
import RocketSim as rsim
import rlgym.rocket_league.math as rlmath
from rlgym.rocket_league.sim import RocketSimEngine
from rlgym.rocket_league.common_values import GOAL_THRESHOLD
from ..utils.math import distance_to_goal

# Hacky way to use the RocketSim engine installation from rlgym
sim = RocketSimEngine()
sim.close()

class BallSimulator:
    def __init__(self):
        self.arena = rsim.Arena(rsim.GameMode.SOCCAR)
        self.team = None
        self.is_shot = False
        self.on_goal = False
        self.params = {
            "shot_threshold": 500, # uu
        }
    
    def update_ball(self, ball_data: pd.Series):
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
        
        self.arena.ball.set_state(ball_state)
    
    def simulate(
        self,
        time: float=1,
        break_if_goal: bool=True,
        break_if_wrong_direction: bool=True
    ):
        self.is_shot = False
        self.on_goal = False
        tick_rate = round(self.arena.tick_rate)
        ticks = round(tick_rate*time)
        
        # Get the direction pointing away from the opponents net
        if self.team != None:
            goal_direction = 1 if self.team else -1
        else:
            goal_direction = None
            
        self.sim_data = []
        for _ in range(ticks):
            self.arena.step(1)
            ball_state = self.arena.ball.get_state()
            self.sim_data.append(ball_state)
            
            if goal_direction != None:
                # Detect Shots that aren't necessarily goals
                dist = distance_to_goal(ball_state.pos, not self.team)
                if  dist <= self.params["shot_threshold"]:
                    self.is_shot = True
                
                # Stop the simulation if hit is in the net
                if -goal_direction*ball_state.pos[1] > GOAL_THRESHOLD:
                    self.is_shot = True
                    self.on_goal = True
                    if break_if_goal:
                        break
                    
                # Stop the simulation if hit is going away from net
                if goal_direction * ball_state.vel[1] > 0:
                    if break_if_wrong_direction:
                        break
                
            
        