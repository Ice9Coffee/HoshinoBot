from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Integer, Column, ForeignKey, Time

Base = declarative_base()

indexArgs = {'index': True, 'unique': True, 'nullable': False}


class Clan(Base):
    __tablename__ = 'clan'
    gid = Column(Integer, **indexArgs)
    cid = Column(Integer, **indexArgs)
    name = Column(String, nullable=False)
    server = Column(Integer, index=True)


class Member(Base):
    __tablename__ = 'member'
    uid = Column(Integer, **indexArgs)
    alt = Column(Integer, **indexArgs)
    name = Column(String, nullable=False)
    gid = Column(Integer, ForeignKey('clan.gid'), index=True, nullable=False)
    cid = Column(Integer, ForeignKey('clan.cid'), index=True, nullable=False)


class Battle(Base):
    __tablename__: str
    eid = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey('member.uid'), index=True)
    alt = Column(Integer, ForeignKey('member.alt'), index=True)
    time = Column(Time, index=True, nullable=False)
    round = Column(Integer, index=True, nullable=False)
    boss = Column(Integer, index=True, nullable=False)
    dmg = Column(Integer, index=True, nullable=False)
    flag = Column(Integer, index=True, nullable=False)