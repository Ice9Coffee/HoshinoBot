import os
from functools import partial, wraps
from typing import Any, Callable, List, Optional, Dict
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import MetaData, Table
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from hoshino.log import logger

from ..exception import AlreadyExistError, DatabaseError, NotFoundError
from . import models, tables

DB_PATH = os.path.expanduser("~/.hoshino/clanbattle.db")
ItemDict_T = Dict[str, Any]


def exceptError(
    function: Optional[Callable] = None,
    raiseException: bool = True,
    prompt: Optional[str] = None,
) -> Callable:
    if function is None:
        return partial(exceptError, raiseException=raiseException, prompt=prompt)

    @wraps(function)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return function(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f"[{function.__qualname__}] {e}")
            if raiseException:
                raise DatabaseError(prompt or "数据库请求失败")
            else:
                return None

    return wrapper


class SqliteDao(object):
    def __init__(self, table: tables.Base):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.table = table
        self._engine = create_engine(f"sqlite://{DB_PATH}")
        self._sessionFactory = sessionmaker(
            bind=self._engine, autocommit=True, autoflush=True
        )
        self._create_table()

    def _create_table(self):
        table: Table = self.table.__table__
        data: MetaData = table.metadata
        data.create_all(bind=self._engine, tables=[table])

    def _connect(self):
        class Transaction:
            def __init__(self, session: Session):
                self._session = session

            def __enter__(self) -> Session:
                self._transaction = self._session.begin(subtransactions=True).__enter__
                return self._session

            def __exit__(self, *args):
                self._transaction.__exit__(*args)

        return Transaction(session=self._sessionFactory)


class ClanDao(SqliteDao):

    SERVER_JP = 0x00
    SERVER_TW = 0x01
    SERVER_CN = 0x02

    def __init__(self):
        super().__init__(table=tables.Clan)
        self.table: tables.Clan

    @exceptError(prompt="添加工会失败")
    def add(self, clan: ItemDict_T):
        clanData = models.ClanItem(**clan)
        with self._connect() as session:
            session.add(self.table(**clanData.dict()))

    @exceptError(prompt="删除工会失败")
    def delete(self, gid: int, cid: int):
        with self._connect() as session:
            queryResult = (
                session.query(self.table)
                .filter(self.table.gid == gid)
                .filter(self.table.cid == cid)
                .first()
            )
            if not queryResult:
                raise NotFoundError
            session.delete(queryResult)

    @exceptError(prompt="修改工会失败")
    def modify(self, clan: ItemDict_T):
        clanData = models.ClanItem(**clan)
        with self._connect() as session:
            queryResult = (
                session.query(self.table)
                .filter(self.table.gid == clanData.gid)
                .filter(self.table.cid == clanData.cid)
                .first()
            )
            if not queryResult:
                raise NotFoundError
            for k, v in clanData.dict(exclude={"cid", "gid"}).items():
                setattr(queryResult, k, v)

    @exceptError(prompt="查找公会失败")
    def find_one(self, gid: int, cid: int) -> models.ClanItem:
        with self._connect() as session:
            queryResult = (
                session.query(self.table)
                .filter(self.table.gid == gid)
                .filter(self.table.cid == cid)
                .first()
            )
            if not queryResult:
                raise NotFoundError
            item = models.ClanItem(**models.DB2Dict(queryResult))
        return item

    @exceptError(prompt="查找公会失败")
    def find_all(self) -> List[models.ClanItem]:
        with self._connect as session:
            queryResult = session.query(self.table).all()
            items = [models.ClanItem(**models.DB2Dict(i)) for i in queryResult]
        return items

    @exceptError(prompt="查找公会失败")
    def find_by_gid(self, gid: int) -> List[models.ClanItem]:
        with self._connect as session:
            queryResult = session.query(self.table).filter(self.table.gid == gid).all()
            items = [models.ClanItem(**models.DB2Dict(i)) for i in queryResult]
        return items


class MemberDao(SqliteDao):
    def __init__(self):
        super.__init__(table=tables.Member)
        self.table: tables.Member

    @exceptError(prompt="添加成员失败")
    def add(self, member: ItemDict_T):
        memberData = models.MemberItem(**member)
        with self._connect() as session:
            session.add(self.table(**dict(memberData)))

    @exceptError(prompt="删除成员失败")
    def delete(self, uid: int, alt: int):
        with self._connect() as session:
            queryResult = (
                session.query(self.table)
                .filter(self.table.uid == uid)
                .filter(self.table.alt == alt)
                .first()
            )
            if not queryResult:
                raise NotFoundError
            session.delete(queryResult)

    @exceptError(prompt="修改成员失败")
    def modify(self, member: ItemDict_T):
        memberData = models.MemberItem(**member)
        with self._connect as session:
            queryResult = (
                session.query(self.table)
                .filter(self.table.uid == memberData.uid)
                .filter(self.table.alt == memberData.alt)
                .first()
            )
            if not queryResult:
                raise NotFoundError
            for k, v in memberData.dict(exclude={"uid", "alt"}).items():
                setattr(queryResult, k, v)

    @exceptError(prompt="查找成员失败")
    def find_one(self, uid: int, alt: int) -> models.MemberItem:
        with self._connect as session:
            queryResult = (
                session.query(self.table)
                .filter(self.table.uid == uid)
                .filter(self.table.alt == alt)
                .first()
            )
            if not queryResult:
                raise NotFoundError
            item = models.MemberItem(**models.DB2Dict(queryResult))
        return item

    @exceptError(prompt="查找成员失败")
    def find_all(self) -> List[models.MemberItem]:
        with self._connect as session:
            queryResult = session.query(self.table).all()
            if not queryResult:
                raise NotFoundError
            items = [models.MemberItem(**models.DB2Dict(i)) for i in queryResult]
        return items

    @exceptError(prompt="查找成员失败")
    def find_by(
        self,
        gid: Optional[int] = None,
        cid: Optional[int] = None,
        uid: Optional[int] = None,
    ) -> List[models.MemberItem]:
        assert gid or cid or uid
        with self._connect as session:
            queryResult = (
                session.query(self.table)
                .filter((self.table.gid == gid) if gid is not None else True)
                .filter((self.table.cid == cid) if cid is not None else True)
                .filter((self.table.uid == uid) if uid is not None else True)
                .all()
            )
            if not queryResult:
                raise NotFoundError
            items = [models.MemberItem(**models.DB2Dict(i)) for i in queryResult]
        return items

    @exceptError(prompt="删除成员的条件有误")
    def delete_by(
        self,
        gid: Optional[int] = None,
        cid: Optional[int] = None,
        uid: Optional[int] = None,
    ):
        assert gid or cid or uid
        with self._connect as session:
            queryResult = (
                session.query(self.table)
                .filter((self.table.gid == gid) if gid is not None else True)
                .filter((self.table.cid == cid) if cid is not None else True)
                .filter((self.table.uid == uid) if uid is not None else True)
                .all()
            )
            if not queryResult:
                raise NotFoundError
            for i in queryResult:
                session.delete(i)
        return


class BattleDao(SqliteDao):
    NORM = 0x00
    LAST = 0x01
    EXT = 0x02
    TIMEOUT = 0x04

    def __init__(self, gid, cid, yyyy, mm):
        table = tables.Battle
        table.__tablename__ = "battle_%d_%d_%04d%02d" % (gid, cid, yyyy, mm)
        super().__init__(table=table)
        self.table: tables.Battle

    @exceptError(prompt="添加记录失败")
    def add(self, challenge: ItemDict_T) -> int:
        battleData = models.BattleItem(**challenge)
        with self._connect as session:
            tableData = self.table(**battleData.dict(exclude={"eid"}))
            session.add(tableData)
            session.flush()
            id = tableData.eid
        return id

    @exceptError(prompt="删除记录失败")
    def delete(self, eid: int):
        with self._connect() as session:
            queryResult = (
                session.query(self.table).filter(self.table.eid == eid).first()
            )
            if not queryResult:
                raise NotFoundError
            session.delete(queryResult)
        return

    @exceptError(prompt="修改记录失败")
    def modify(self, challenge: ItemDict_T):
        battleData = models.BattleItem(**challenge)
        with self._connect() as session:
            queryResult = (
                session.query(self.table)
                .filter(self.table.eid == battleData.eid)
                .first()
            )
            if not queryResult:
                raise NotFoundError
            for k, v in battleData.dict(exclude={"eid"}).items():
                setattr(queryResult, k, v)
        return

    @exceptError(prompt="查找记录失败")
    def find_one(self, eid: int) -> models.BattleItem:
        with self._connect() as session:
            queryResult = (
                session.query(self.table).filter(self.table.eid == eid).first()
            )
            if not queryResult:
                raise NotFoundError
            item = models.BattleItem(**models.DB2Dict(queryResult))
        return item

    @exceptError(prompt="查找记录失败")
    def find_all(self) -> List[models.BattleItem]:
        with self._connect() as session:
            queryResult = session.query(self.table).all()
            if not queryResult:
                raise NotFoundError
            items = [models.BattleItem(**models.DB2Dict(i)) for i in queryResult]
        return items

    @exceptError(prompt="查找记录失败")
    def find_by(
        self,
        uid: Optional[int] = None,
        alt: Optional[int] = None,
        order_by_user: bool = False,
    ) -> List[models.BattleItem]:
        assert uid or alt
        with self._connect as session:
            queryResult = (
                session.query(self.table)
                .filter((self.table.uid == uid) if uid is not None else True)
                .filter((self.table.alt == alt) if alt is not None else True)
                .order_by(self.table.round if not order_by_user else self.table.uid)
                .all()
            )
            if not queryResult:
                raise NotFoundError
            items = [models.BattleItem(**models.DB2Dict(i)) for i in queryResult]
        return items
