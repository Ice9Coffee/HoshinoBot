from pydantic import BaseModel

from typing import Any, Dict, Optional
from datetime import datetime


def DB2Dict(db: Any) -> Dict[str, Any]:
    return dict(db.__dict__)


class ItemBase(BaseModel):
    def __getitem__(self, key: str):
        return dict(self).__getitem__(key)

    def __setitem__(self, key: str, value: Any):
        setattr(self, key, value)


class ClanItem(ItemBase):
    gid: int
    cid: int
    name: str
    server: int


class MemberItem(ItemBase):
    uid: int
    alt: int
    name: str
    gid: int
    cid: int


class BattleItem(ItemBase):
    eid: Optional[int] = None
    uid: int
    alt: int
    time: datetime
    round: int
    boss: int
    dmg: int
    flag: int