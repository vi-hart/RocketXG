from sqlalchemy.sql import or_
from sqlalchemy.orm import Query
from .models import *

def join_all_tables(query: Query):
    return (
        query.select_from(Replay).join(Match)\
        .outerjoin(Round, Match.round_id == Round.id)\
        .outerjoin(Group, Round.group_id == Group.id)\
        .outerjoin(StageFromRound, Round.stage_id == StageFromRound.id)\
        .outerjoin(StageFromGroup, Group.stage_id == StageFromGroup.id)\
        .outerjoin(EventFromMatch, Match.event_id == EventFromMatch.id)\
        .outerjoin(
            EventFromStage,
            or_(
                StageFromRound.event_id == EventFromStage.id,
                StageFromGroup.event_id == EventFromStage.id,
            )
        )\
        .outerjoin(Region, or_(
            EventFromStage.region_id == Region.id,
            EventFromMatch.region_id == Region.id,
        ))\
        .outerjoin(SplitFromEvent, or_(
            EventFromStage.split_id == SplitFromEvent.id,
            EventFromMatch.split_id == SplitFromEvent.id,
        ))\
        .outerjoin(SplitFromRegion, Region.split_id == SplitFromRegion.id)\
        .join(Season, or_(
            SplitFromEvent.season_id == Season.id,
            SplitFromRegion.season_id == Season.id
        ))
    )