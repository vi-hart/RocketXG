from typing import List
from bisect import bisect_left
from rlgym_tools.rocket_league.replays.parsed_replay import ParsedReplay

from .base import Hit, Possession, PossessionChain
from ..simulator.ball_simulator import BallSimulator

def find_goal_hits(replay: ParsedReplay, hits: List[Hit]):
    hit_frames = [hit.frame_number for hit in hits]
    goals = replay.metadata["game"]["goals"]
    for goal in goals:
        start_search = bisect_left(hit_frames, goal["frame"])
        for i in range(start_search - 1, 0, -1):
            if hits[i].team == goal["is_orange"]:
                hits[i].hit_type = "goal"
                break
            

def detect_shots(chains: List[PossessionChain], time: float=1):
    simulator = BallSimulator()
    shots = 0
    for chain in chains:
        last_hit = chain.possessions[-1].hits[-1]
        # Skip shots we know are goals
        if last_hit.hit_type == "goal":
            continue
        
        simulator.team = last_hit.team
        simulator.update_ball(last_hit.ball_data)
        simulator.simulate(time)
        
        if simulator.is_shot:
            shots += 1
            last_hit.hit_type = "shot"
            last_hit.metadata["on_goal"] = simulator.on_goal
    print(f"num_shots: {shots}")
            