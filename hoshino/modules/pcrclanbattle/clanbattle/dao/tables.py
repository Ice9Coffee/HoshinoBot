from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Integer, Column, ForeignKey, DateTime
from uuid import uuid4

Base = declarative_base()


class Clan(Base):
    __tablename__ = "clan"
    gid = Column(Integer, primary_key=True)
    cid = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    server = Column(Integer, nullable=False)


class Member(Base):
    __tablename__ = "member"
    uid = Column(Integer, primary_key=True)
    alt = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    gid = Column(Integer, ForeignKey("clan.gid"), nullable=False)
    cid = Column(Integer, ForeignKey("clan.cid"), nullable=False)


class Battle(Base):
    __tablename__ = "battle"
    eid = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey("member.uid"))
    alt = Column(Integer, ForeignKey("member.alt"))
    time = Column(DateTime, nullable=False)
    round = Column(Integer, nullable=False)
    boss = Column(Integer, nullable=False)
    dmg = Column(Integer, nullable=False)
    flag = Column(Integer, nullable=False)


class PlannedDamage(Base):
    __tablename__ = "planned_damage"
    pid = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey("member.uid"),nullable=False)
    alt = Column(Integer, ForeignKey("member.alt"),nullable=False)
    dmg = Column(Integer,nullable=False)
    boss = Column(Integer,nullable=False)
    type = Column(Integer,nullable=False)
