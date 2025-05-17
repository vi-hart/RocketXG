import hashlib
from progress.bar import IncrementalBar
from rlgym_tools.rocket_league.replays.parsed_replay import process_replay
from typing import Dict, List
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import (
    Season,
    Split,
    Region,
    Event,
    Stage,
    Group,
    Round,
    Match,
    Replay,
    Base
)


def _check_any(checks: List[str], string: str) -> bool:
    return any(check in string.lower() for check in checks)


def _parse_latest_structure(path: Path) -> Dict:
    _splits = ["worlds", "major",
               "fall", "spring", "winter", "finals"]
    _stages = ["single elimination", "swiss",
               "playoffs", "groups", "upper", "lower"]
    _events = ["qualifiers", "main event", "major",
               "wilcard", "tiebreakers", "regional"]
    _regions = ["america", "europe"]
    _rounds = ["round ", "finals"]

    def _get_dir_len(path: Path) -> int:
        parts = path.parts
        try:
            for i in [9, 8, 7, 6]:
                if _check_any(_splits, parts[-i]):
                    return i + 1
        except:
            pass
        raise ValueError(
            "This structure is not supported. Make sure to use the right version.")

    dir_len = _get_dir_len(path)
    parts = path.parts[-dir_len:]
    structure = {
        "raw_path": path,
        "season_name": parts[0],
        "split_name": parts[1]
    }
    for part in parts[2:]:
        if "vs" in part.lower():
            structure["match_name"] = part
        if _check_any(_rounds, part):
            structure["round_name"] = part
        if "group " in part.lower():
            structure["group_name"] = part
        if _check_any(_stages, part):
            structure["stage_name"] = part
        if _check_any(_events, part):
            structure["event_name"] = part
        if _check_any(_regions, part):
            structure["region_name"] = part

    return structure


def parse_directory_structure(path: Path, version: str = "latest") -> Dict:
    """Extracts RLCS hierarchy and unifies different Season structures."""
    _supported_versions = ["2023", "2024"]
    match version:
        case "2023" | "2024" | "latest":
            return _parse_latest_structure(path)
        case _:
            raise ValueError(
                f"Invalid version: {version}. Supported versions: {_supported_versions}"
            )


class RLCSParser:
    def __init__(
        self, database_url: str = "sqlite:///rlcs.db",
        parsed_dir: str = "./parsed"
    ):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.parsed_dir = Path(parsed_dir)

        Base.metadata.create_all(self.engine)

    def _get_or_create(self, session: Session, model, **kwargs):
        instance = session.query(model).filter_by(**kwargs).first()
        if not instance:
            instance = model(**kwargs)
            session.add(instance)
            session.commit()
        return instance

    def process_replay(self, replay_path: Path, version: str = "latest"):
        hierarchy = parse_directory_structure(replay_path, version=version)
        teams = self._parse_match_name(hierarchy.get("match_name"))

        with Session(self.engine) as session:
            try:
                season = self._get_or_create(
                    session, Season,
                    name=hierarchy.get("season_name")
                )

                split = self._get_or_create(
                    session, Split,
                    season=season,
                    name=hierarchy.get("split_name"),
                )

                region = None
                region_name = hierarchy.get("region_name")
                if region_name:
                    region = self._get_or_create(
                        session, Region,
                        split=split,
                        name=region_name
                    )

                event = self._get_or_create(
                    session, Event,
                    region=region,
                    split=split,
                    name=hierarchy.get("event_name")
                )

                stage = None
                group = None
                round = None
                stage_name = hierarchy.get("stage_name")
                if stage_name:
                    stage = self._get_or_create(
                        session, Stage,
                        event=event,
                        name=stage_name
                    )

                    group_name = hierarchy.get("group_name")
                    if group_name:
                        group = self._get_or_create(
                            session, Group,
                            stage=stage,
                            name=group_name
                        )

                    round_name = hierarchy.get("round_name")
                    if round_name:
                        round = self._get_or_create(
                            session, Round,
                            group=group,
                            stage=stage,
                            name=round_name
                        )

                match = self._get_or_create(
                    session, Match,
                    round=round,
                    event=event,
                    name=hierarchy.get("match_name"),
                    team1=teams["team1"],
                    team2=teams["team2"]
                )

                replay_hash = self._generate_replay_hash(replay_path)
                parsed_path = self._get_parsed_path(replay_hash)
                print(f"Processing {replay_path} at {parsed_path}")
                process_replay(replay_path=replay_path, output_folder=parsed_path)
                
                if session.query(Replay).get(replay_hash):
                    print(f"Skipping duplicate replay: {replay_path}")
                    return

                replay = Replay(
                    hash=replay_hash,
                    match=match,
                    game_number=self._extract_game_number(replay_path.name),
                    raw_path=str(replay_path),
                    parsed_path=str(parsed_path)
                )
                
                session.add(replay)
                session.commit()
                print(f"Processed {replay_path} successfully")

            except Exception as e:
                session.rollback()
                print(f"Failed to process {replay_path}: {str(e)}")
                raise

    def _get_parsed_path(self, replay_hash: str) -> Path:
        return self.parsed_dir / replay_hash

    @staticmethod
    def _parse_match_name(name: str) -> Dict:
        try:
            team1, team2 = name.split(" vs ")
            return {"team1": team1, "team2": team2}
        except ValueError:
            return {"team1": "Unknown", "team2": "Unknown"}

    @staticmethod
    def _generate_replay_hash(path: Path) -> str:
        with open(path, "rb") as file:
            return hashlib.sha256(file.read()).hexdigest()
        
    @staticmethod
    def _extract_game_number(filename: str) -> int:
        try: return int(''.join(filter(str.isdigit, filename)))
        except: return -1

    def process_directory(self, root_dir: str, version: str = "latest"):
        """Process all replays in a directory structure"""
        root_path = Path(root_dir)
        replay_paths = [
            path for path in root_path.glob("**/*.replay")
            if path.is_file()
        ]
        
        for replay_path in IncrementalBar('Collecting games').iter(replay_paths):
            try:
                self.process_replay(replay_path, version=version)
            except Exception as e:
                print(f"Skipping {replay_path}: {str(e)}")