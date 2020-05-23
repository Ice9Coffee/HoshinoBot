import os
from functools import partial, wraps
from typing import Any, Callable, List, Optional
from urllib.parse import urlsplit

from sqlalchemy import Table
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from hoshino.log import logger

from ..exception import AlreadyExistError, DatabaseError, NotFoundError
from . import models, tables

#DB_PATH = os.path.expanduser('~/.hoshino/clanbattle.db')
DB_URI = 'sqlite://~/.hoshino/clanbattle.db'


def exceptError(function: Optional[Callable] = None,
                raiseException: bool = True,
                prompt: Optional[str] = None) -> Callable:
    if function is None:
        return partial(raiseException=raiseException)

    @wraps(function)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return function(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f'[{function.__qualname__}] {e}')
            if raiseException:
                raise DatabaseError(prompt or '数据库请求失败')
            else:
                return None

    return wrapper


class SqliteDao(object):
    def __init__(self, table: tables.Base):
        os.makedirs(os.path.dirname(urlsplit(DB_URI).path), exist_ok=True)
        self.table = table
        self._engine = create_engine(DB_URI)
        self._sessionFactory = sessionmaker(bind=self._engine,
                                            autocommit=True,
                                            autoflush=True)
        self._create_table()

    def _create_table(self):
        data: Table = self.table.__table__
        data.metadata.create_all(bind=self._engine)

    def _connect(self):
        class Transaction:
            def __init__(self, session: Session):
                self._session = session

            def __enter__(self):
                self._transaction = self._session.begin(
                    subtransactions=True).__enter__
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

    @exceptError(prompt='添加工会失败')
    def add(self, clan: dict):
        clanData = models.ClanItem(**clan)
        with self._connect() as session:
            session.add(self.table(**dict(clanData)))

    @exceptError
    def delete(self, gid: int, cid: int):
        with self._connect() as session:
            queryResult = session.query(self.table).filter(
                self.table.gid == gid).filter(self.table.cid == cid).first()
            if not queryResult:
                raise NotFoundError
            session.delete(queryResult)

    @exceptError
    def modify(self, clan: dict):
        clanData = models.ClanItem(**clan)
        with self._connect() as session:
            queryResult = session.query(
                self.table).filter(self.table.gid == clanData.gid).filter(
                    self.table.cid == clanData.cid).first()
            if not queryResult:
                raise NotFoundError
            for k, v in dict(clanData):
                setattr(queryResult, k, v)

    @exceptError(prompt='查找公会失败')
    def find_one(self, gid: int, cid: int) -> models.ClanItem:
        with self._connect() as session:
            queryResult = session.query(self.table).filter(
                self.table.gid == gid).filter(self.table.cid == cid).first()
            if not queryResult:
                raise NotFoundError
            item = models.ClanItem(**models.DB2Dict(queryResult))
        return item

    @exceptError(prompt='查找公会失败')
    def find_all(self) -> List[models.ClanItem]:
        with self._connect as session:
            queryResult = session.query(self.table).all()
            items = [models.ClanItem(**models.DB2Dict(i)) for i in queryResult]
        return items

    @exceptError(prompt='查找公会失败')
    def find_by_gid(self, gid: int) -> List[models.ClanItem]:
        with self._connect as session:
            queryResult = session.query(
                self.table).filter(self.table.gid == gid).all()
            items = [models.ClanItem(**models.DB2Dict(i)) for i in queryResult]
        return items


class MemberDao(SqliteDao):
    def __init__(self):
        super().__init__(table='member',
                         columns='uid, alt, name, gid, cid',
                         fields='''
            uid INT NOT NULL,
            alt INT NOT NULL,
            name TEXT NOT NULL,
            gid INT NOT NULL,
            cid INT NOT NULL,
            PRIMARY KEY (uid, alt)
            ''')

    @staticmethod
    def row2item(r):
        return {
            'uid': r[0],
            'alt': r[1],
            'name': r[2],
            'gid': r[3],
            'cid': r[4]
        } if r else None

    def add(self, member):
        with self._connect() as conn:
            try:
                conn.execute(
                    '''
                    INSERT INTO {0} ({1}) VALUES (?, ?, ?, ?, ?)
                    '''.format(self._table, self._columns),
                    (member['uid'], member['alt'], member['name'],
                     member['gid'], member['cid']))
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.add] {e}')
                raise DatabaseError('添加成员失败')

    def delete(self, uid, alt):
        with self._connect() as conn:
            try:
                conn.execute(
                    '''
                    DELETE FROM {0} WHERE uid=? AND alt=?
                    '''.format(self._table), (uid, alt))
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.delete] {e}')
                raise DatabaseError('删除成员失败')

    def modify(self, member):
        with self._connect() as conn:
            try:
                conn.execute(
                    '''
                    UPDATE {0} SET name=?, gid=?, cid=? WHERE uid=? AND alt=?
                    '''.format(self._table),
                    (member['name'], member['gid'], member['cid'],
                     member['uid'], member['alt']))
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.modify] {e}')
                raise DatabaseError('修改成员失败')

    def find_one(self, uid, alt):
        with self._connect() as conn:
            try:
                ret = conn.execute(
                    '''
                    SELECT {1} FROM {0} WHERE uid=? AND alt=?
                    '''.format(self._table, self._columns),
                    (uid, alt)).fetchone()
                return self.row2item(ret)
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.find_one] {e}')
                raise DatabaseError('查找成员失败')

    def find_all(self):
        with self._connect() as conn:
            try:
                ret = conn.execute(
                    '''
                    SELECT {1} FROM {0}
                    '''.format(self._table, self._columns), ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.find_all] {e}')
                raise DatabaseError('查找成员失败')

    def find_by(self, gid=None, cid=None, uid=None):
        cond_str = []
        cond_tup = []
        if not gid is None:
            cond_str.append('gid=?')
            cond_tup.append(gid)
        if not cid is None:
            cond_str.append('cid=?')
            cond_tup.append(cid)
        if not uid is None:
            cond_str.append('uid=?')
            cond_tup.append(uid)

        if 0 == len(cond_tup):
            return self.find_all()

        cond_str = " AND ".join(cond_str)

        with self._connect() as conn:
            try:
                ret = conn.execute(
                    '''
                    SELECT {1} FROM {0} WHERE {2}
                    '''.format(self._table, self._columns, cond_str),
                    cond_tup).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.find_by] {e}')
                raise DatabaseError('查找成员失败')

    def delete_by(self, gid=None, cid=None, uid=None):
        cond_str = []
        cond_tup = []
        if not gid is None:
            cond_str.append('gid=?')
            cond_tup.append(gid)
        if not cid is None:
            cond_str.append('cid=?')
            cond_tup.append(cid)
        if not uid is None:
            cond_str.append('uid=?')
            cond_tup.append(uid)

        if 0 == len(cond_tup):
            raise DatabaseError('删除成员的条件有误')

        cond_str = " AND ".join(cond_str)

        with self._connect() as conn:
            try:
                cur = conn.execute(
                    '''
                    DELETE FROM {0} WHERE {1}
                    '''.format(self._table, cond_str), cond_tup)
                return cur.rowcount
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.find_by] {e}')
                raise DatabaseError('查找成员失败')


class BattleDao(SqliteDao):
    NORM = 0x00
    LAST = 0x01
    EXT = 0x02
    TIMEOUT = 0x04

    def __init__(self, gid, cid, yyyy, mm):
        super().__init__(table=self.get_table_name(gid, cid, yyyy, mm),
                         columns='eid, uid, alt, time, round, boss, dmg, flag',
                         fields='''
            eid INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INT NOT NULL,
            alt INT NOT NULL,
            time TIMESTAMP NOT NULL,
            round INT NOT NULL,
            boss  INT NOT NULL,
            dmg   INT NOT NULL,
            flag  INT NOT NULL
            ''')

    @staticmethod
    def get_table_name(gid, cid, yyyy, mm):
        return 'battle_%d_%d_%04d%02d' % (gid, cid, yyyy, mm)

    @staticmethod
    def row2item(r):
        return {
            'eid': r[0],
            'uid': r[1],
            'alt': r[2],
            'time': r[3],
            'round': r[4],
            'boss': r[5],
            'dmg': r[6],
            'flag': r[7]
        } if r else None

    def add(self, challenge):
        with self._connect() as conn:
            try:
                cur = conn.execute(
                    '''
                    INSERT INTO {0} ({1}) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)
                    '''.format(self._table, self._columns),
                    (challenge['uid'], challenge['alt'], challenge['time'],
                     challenge['round'], challenge['boss'], challenge['dmg'],
                     challenge['flag']))
                return cur.lastrowid
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[BattleDao.add] {e}')
                raise DatabaseError('添加记录失败')

    def delete(self, eid):
        with self._connect() as conn:
            try:
                conn.execute(
                    '''
                    DELETE FROM {0} WHERE eid=?
                    '''.format(self._table), (eid, ))
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[BattleDao.delete] {e}')
                raise DatabaseError('删除记录失败')

    def modify(self, challenge):
        with self._connect() as conn:
            try:
                conn.execute(
                    '''
                    UPDATE {0} SET uid=?, alt=?, time=?, round=?, boss=?, dmg=?, flag=? WHERE eid=?
                    '''.format(self._table),
                    (challenge['uid'], challenge['alt'], challenge['time'],
                     challenge['round'], challenge['boss'], challenge['dmg'],
                     challenge['flag'], challenge['eid']))
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[BattleDao.modify] {e}')
                raise DatabaseError('修改记录失败')

    def find_one(self, eid):
        with self._connect() as conn:
            try:
                ret = conn.execute(
                    '''
                    SELECT {1} FROM {0} WHERE eid=?
                    '''.format(self._table, self._columns),
                    (eid, )).fetchone()
                return self.row2item(ret)
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[BattleDao.find_one] {e}')
                raise DatabaseError('查找记录失败')

    def find_all(self):
        with self._connect() as conn:
            try:
                ret = conn.execute(
                    '''
                    SELECT {1} FROM {0} ORDER BY round, boss, eid
                    '''.format(self._table, self._columns), ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[BattleDao.find_all] {e}')
                raise DatabaseError('查找记录失败')

    def find_by(self, uid=None, alt=None, order_by_user=False):
        cond_str = []
        cond_tup = []
        order = 'round, boss, eid' if not order_by_user else 'uid, alt, round, boss, eid'
        if not uid is None:
            cond_str.append('uid=?')
            cond_tup.append(uid)
        if not alt is None:
            cond_str.append('alt=?')
            cond_tup.append(alt)
        if 0 == len(cond_tup):
            return self.find_all()

        cond_str = " AND ".join(cond_str)

        with self._connect() as conn:
            try:
                ret = conn.execute(
                    '''
                    SELECT {1} FROM {0} WHERE {2} ORDER BY {3}
                    '''.format(self._table, self._columns, cond_str, order),
                    cond_tup).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[BattleDao.find_by] {e}')
                raise DatabaseError('查找记录失败')
