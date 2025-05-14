from typing import List
from rlgym_tools.rocket_league.replays.parsed_replay import ParsedReplay
from bisect import bisect_left
from .player import Player, generate_players


class Hit:
    def __init__(
        self,
        frame: int | None = None,
        player_id: int | None = None,
        player: Player | None = None,
        player_changed: bool = False,
        team_changed: bool = False,
        is_goal: bool = False,
        is_shot: bool = False
    ):
        self.frame = frame
        self.player_id = player_id
        self.player = player
        self.player_changed = player_changed
        self.team_changed = team_changed
        self.is_goal = is_goal
        self.is_shot = is_shot

        if player:
            self.player_id = player.id


def find_goal_hits(replay: ParsedReplay):
    """
    Finds the hits which lead to goals.
    
    A list of hits is generated in order of frame number. The last hit from the team that scored is marked as a goal for each goal in a replay. The modified list of hits is then returned.
    """
    hits = replay.analyzer["hits"]
    hit_frames = [hit["frame_number"] for hit in hits]
    players = {player.id: player for player in generate_players(replay)}
    goals = replay.metadata["game"]["goals"]
    for goal in goals:
        is_orange = goal["is_orange"]
        start_search = bisect_left(hit_frames, goal["frame"])
        for i in range(start_search-1, 0, -1):
            hit = hits[i]
            player = players[hit["player_unique_id"]]
            if player.is_orange == is_orange:
                hit["is_goal"] = True
                break
    return hits


def generate_hits_table(replay: ParsedReplay):
    """
    Hit data is extracted into a dictionary keyed by Player objects whose corresponding hits are stored as lists of Hit objects.
    """
    hits_list = find_goal_hits(replay)
    player_table = {player.id: player for player in generate_players(replay)}
    hits_table = {player: [] for player in player_table.values()}
    
    player_changed = False
    team_changed = False
    previous_player_id = None
    previous_team_is_orange = None
    
    for hit_dict in hits_list:
        player = player_table[hit_dict["player_unique_id"]]
        
        player_changed = False if previous_player_id == player.id else True
        team_changed = False if previous_team_is_orange == player.is_orange else True
        previous_player_id = player.id
        previous_team_is_orange = player.is_orange
        
        is_goal = hit_dict.get("is_goal", False)
        hit = Hit(
            frame=hit_dict["frame_number"],
            player=player,
            player_changed=player_changed,
            team_changed=team_changed,
            is_goal=is_goal,
            is_shot=is_goal
        )
        hits_table[player].append(hit)
        
    for player, hits in hits_table.items():
        player.all_hits = hits
        
    return hits_table
