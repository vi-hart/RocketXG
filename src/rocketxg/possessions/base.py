
from dataclasses import dataclass
from typing import List, Set, Optional


@dataclass
class Hit:
    frame_number: int
    player_id: str
    team: str
    ball_data: dict
    player_state: dict
    hit_type: str = None  # 'shot', 'pass', 'dribble', 'aerial', 'clearance'
    outcome: str = None   # 'goal', 'save', 'post', 'wide'
    metadata: dict = None


@dataclass
class Possession:
    start_frame: int
    end_frame: int
    player_id: int
    team: str
    hits: List[Hit]
    duration: float = 0  # seconds
    possession_type: str = None  # TODO: 'organized', 'counter', 'fifty-fifty'
    chain_id: Optional[int] = None

    @property
    def num_hits(self):
        return len(self.hits)


@dataclass
class PossessionChain:
    start_frame: int
    end_frame: int
    players: Set[str]
    team: str
    possessions: List[Possession]
    duration: float = 0  # seconds
    outcome: str = None  # 'shot', 'goal', 'turnover', 'clearance'

    @property
    def num_hits(self):
        return sum([possession.num_hits for possession in self.possessions])

    @property
    def num_players(self):
        return len(self.players)
