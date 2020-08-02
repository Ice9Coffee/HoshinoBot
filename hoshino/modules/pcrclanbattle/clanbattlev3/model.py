from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Clan:
    gid:int
    name:str
    server:int


@dataclass
class Member:
    uid:int
    gid:int
    name:str

@dataclass
class Challenge:
    eid:int
    uid:int
    time:datetime
    round:int
    boss:int
    dmg:int
    flag:int


@dataclass
class Progress:
    round:int
    boss:int
    hp:int

@dataclass
class PauseRecord:
    uid:int
    dmg:int
    second_left:int


@dataclass
class Subscribe:
    uid:int
    round:int
    boss:int
    memo:str


@dataclass
class SosRecord:
    uid:int
    time:datetime
    round:int
    boss:int


@dataclass
class SLRecord:
    uid:int
    time:datetime
    round:int
    boss:int
