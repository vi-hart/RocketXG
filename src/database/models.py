from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, aliased

Base = declarative_base()


class Season(Base):
    __tablename__ = 'seasons'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32))
    start_date = Column(Date)
    end_date = Column(Date)
    splits = relationship("Split", back_populates="season")


class Split(Base):
    __tablename__ = 'splits'
    id = Column(Integer, primary_key=True, autoincrement=True)
    season_id = Column(Integer, ForeignKey('seasons.id'))
    name = Column(String(32))

    season = relationship("Season", back_populates="splits")
    regions = relationship("Region", back_populates="split")
    events = relationship("Event", back_populates="split")


class Region(Base):
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    split_id = Column(Integer, ForeignKey('splits.id'))
    name = Column(String(32))

    split = relationship("Split", back_populates="regions")
    events = relationship("Event", back_populates="region")


class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    split_id = Column(Integer, ForeignKey("splits.id"))
    name = Column(String(64), nullable=False)
    type = Column(String(32))

    region = relationship("Region", back_populates="events")
    split = relationship("Split", back_populates="events")
    stages = relationship("Stage", back_populates="event")
    matches = relationship("Match", back_populates="event")


class Stage(Base):
    __tablename__ = 'stages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    name = Column(String(64), nullable=False)
    type = Column(String(32))

    event = relationship("Event", back_populates="stages")
    rounds = relationship("Round", back_populates="stage")
    groups = relationship("Group", back_populates="stage")


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True, autoincrement=True)
    stage_id = Column(Integer, ForeignKey("stages.id"))
    name = Column(String(64), nullable=False)

    stage = relationship("Stage", back_populates="groups")
    rounds = relationship("Round", back_populates="group")


class Round(Base):
    __tablename__ = 'rounds'
    id = Column(Integer, primary_key=True, autoincrement=True)
    stage_id = Column(Integer, ForeignKey("stages.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    name = Column(String(32), nullable=False)

    stage = relationship("Stage", back_populates="rounds")
    group = relationship("Group", back_populates="rounds")
    matches = relationship("Match", back_populates="round")


class Match(Base):
    __tablename__ = 'matches'
    id = Column(Integer, primary_key=True, autoincrement=True)
    round_id = Column(Integer, ForeignKey("rounds.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    name = Column(String(64), nullable=False)
    team1 = Column(String(32), nullable=False)
    team2 = Column(String(32), nullable=False)

    round = relationship("Round", back_populates="matches")
    event = relationship("Event", back_populates="matches")
    replays = relationship("Replay", back_populates="match")


class Replay(Base):
    __tablename__ = 'replays'
    hash = Column(String(64), primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    game_number = Column(Integer, nullable=False)
    raw_path = Column(String(255), nullable=False)
    parsed_path = Column(String(255))

    match = relationship("Match", back_populates="replays")

StageFromRound = aliased(Stage)
StageFromGroup = aliased(Stage)
SplitFromEvent = aliased(Split)
SplitFromRegion = aliased(Split)
EventFromMatch = aliased(Event)
EventFromStage = aliased(Event)