from typing import List
from rlgym_tools.rocket_league.replays.parsed_replay import ParsedReplay
from .base import Hit, Possession, PossessionChain
from .analysis import find_goal_hits, detect_shots


class PossessionAnalyzer:
    """Analyzes Ball Possessions in a ParsedReplay
    
    Attributes:
        current_chain (PossessionChain): Current chain of possessions (single team)
        current_possession (Possession): Current possession (single player)
        params (dict): Option parameters for the replay analysis
            - max_possession_gap: maximum number of frames between touches for a possession to count.
            - frames_per_second: number of frames per second the replay is recorded at.
            - shot_time: time into the future hits are simulated and shots are detected.
    """
    def __init__(self):
        self.current_chain: PossessionChain | None = None
        self.current_possession: Possession | None = None
        self.params = {
            "max_possession_gap": 120,  # frames
            "frames_per_second": 30,  # fps
            "shot_time": 2 # s
        }

    def analyze_replay(self, replay: ParsedReplay) -> List[PossessionChain]:
        self.current_chain = None
        self.current_possession = None
        chains = self._generate_possession_chains(replay)
        possessions = [possession for chain in chains for possession in chain.possessions]
        hits = [hit for possession in possessions for hit in possession.hits]
        self._classify_hits(replay, hits)
        self._classify_possessions(replay, possessions)
        self._classify_chains(replay, chains)
        return hits, possessions, chains

    def _generate_possession_chains(self, replay: ParsedReplay) -> List[PossessionChain]:
        chains = []
        current_player = None
        current_team = None
        last_hit_frame = None

        for hit_dict in replay.analyzer["hits"]:
            frame = hit_dict["frame_number"]
            player = hit_dict["player_unique_id"]
            team = self._get_player_team(player, replay)
            hit = Hit(
                frame_number=frame,
                player_id=player,
                team=team,
                ball_data=replay.ball_df.iloc[frame, :],
                player_state=self._get_player_states(frame, replay),
                metadata={}
            )
            frames_since_last = frame - last_hit_frame if last_hit_frame else 0
            last_hit_frame = frame

            if team != current_team or frames_since_last > self.params["max_possession_gap"]:
                self._finalize_possession()
                self._finalize_chain()
                if self.current_chain:
                    chains.append(self.current_chain)

                self._start_possession(hit)
                self._start_chain(self.current_possession)
                current_player = player
                current_team = team

            else:
                if player != current_player:
                    self._finalize_possession()
                    self._start_possession(hit)
                    self.current_chain.possessions.append(
                        self.current_possession
                    )
                    self.current_chain.players.add(player)
                    current_player = player

                else:
                    self.current_possession.end_frame = frame
                    self.current_possession.hits.append(hit)

                self.current_chain.end_frame = frame
                self.current_chain.possessions
        
        self._finalize_possession()
        self._finalize_chain()
        if self.current_chain:
            chains.append(self.current_chain)
        return chains

    def _start_possession(self, hit: Hit) -> None:
        self.current_possession = Possession(
            start_frame=hit.frame_number,
            end_frame=hit.frame_number,
            player_id=hit.player_id,
            team=hit.team,
            hits=[hit]
        )

    def _start_chain(self, possession: Possession) -> None:
        self.current_chain = PossessionChain(
            start_frame=possession.start_frame,
            end_frame=possession.end_frame,
            players={possession.player_id},
            team=possession.team,
            possessions=[possession]
        )

    def _finalize_possession(self):
        """Final calculations on the current Possession"""
        if not self.current_possession:
            return
        
        start = self.current_possession.start_frame
        end = self.current_possession.end_frame
        self.current_possession.duration = self._calculate_duration(start, end)

    def _finalize_chain(self):
        """Final calculations on the current PossessionChain"""
        if not self.current_chain:
            return
        
        start = self.current_chain.start_frame
        end = self.current_chain.end_frame
        self.current_chain.duration = self._calculate_duration(start, end)

    def _calculate_duration(self, start: int, end: int) -> float:
        return (end - start) / self.params["frames_per_second"]

    @staticmethod
    def _get_player_team(player_id: int, replay: ParsedReplay) -> bool:
        for player in replay.metadata["players"]:
            if player["unique_id"] == player_id:
                return player["is_orange"]

    @staticmethod
    def _get_player_states(frame: int, replay: ParsedReplay) -> dict:
        return {
            player: state.iloc[frame, :]
            for player, state in replay.player_dfs.items()
        }
        
    def _classify_hits(self, replay: ParsedReplay, hits: List[Hit]):
        # Find goals (Compare hit frame to game periods)
        find_goal_hits(replay, hits)
    
    def _classify_possessions(self, replay: ParsedReplay, possessions: List[Possession]):
        # Find dribbles (Time between player hits)
        pass
    
    def _classify_chains(self, replay: ParsedReplay, chains: List[PossessionChain]):
        # Find passes (Links between players possessions)
        # Find 50/50s (Links between opponent possessons)
        # Detect Shots (Last hit of a possession chain)
        detect_shots(chains, time=self.params["shot_time"])
        # Detect Saves (Opponent hits after a shot)
        pass
