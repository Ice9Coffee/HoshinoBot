from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Integer, Column, ForeignKey, Time

Base = declarative_base()

nonNullIndex = {'index': True, 'nullable': False}


class Clan(Base):
    __tablename__ = 'clan'
    gid = Column(Integer, primary_key=True)
    cid = Column(Integer, primary_key=True)
    name = Column(String, **nonNullIndex)
    server = Column(Integer, **nonNullIndex)


class Member(Base):
    __tablename__ = 'member'
    uid = Column(Integer, primary_key=True)
    alt = Column(Integer, primary_key=True)
    name = Column(String, **nonNullIndex)
    gid = Column(Integer, ForeignKey('clan.gid'), **nonNullIndex)
    cid = Column(Integer, ForeignKey('clan.cid'), **nonNullIndex)


class Battle(Base):
    __tablename__ = 'battle'
    eid = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey('member.uid'), index=True)
    alt = Column(Integer, ForeignKey('member.alt'), index=True)
    time = Column(Time, **nonNullIndex)
    round = Column(Integer, **nonNullIndex)
    boss = Column(Integer, **nonNullIndex)
    dmg = Column(Integer, **nonNullIndex)
    flag = Column(Integer, **nonNullIndex)