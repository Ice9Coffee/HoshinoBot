import sqlite3
import os
import logging
import datetime

DB_PATH = os.path.join(os.path.expanduser('~'), '.hoshino/clanbattle.db')

class SqliteDao(object):
    def __init__(self, table, columns, fields):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._dbpath = DB_PATH
        self._table = table
        self._columns = columns
        self._fields = fields
        self._create_table()


    def _create_table(self):
        sql = "CREATE TABLE IF NOT EXISTS {0} ({1})".format(self._table, self._fields)
        # logging.getLogger('SqliteDao._create_table').debug(sql)
        with self._connect() as conn:
            conn.execute(sql)


    def _connect(self):
        # detect_types 中的两个参数用于处理datetime
        return sqlite3.connect(self._dbpath, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)



class ClanDao(SqliteDao):

    SERVER_JP = 0x00
    SERVER_TW = 0x01
    SERVER_CN = 0x02

    def __init__(self):
        super().__init__(
            table='clan',
            columns='gid, cid, name, server',
            fields='''
            gid INT NOT NULL,
            cid INT NOT NULL,
            name TEXT NOT NULL,
            server INT NOT NULL,
            PRIMARY KEY (gid, cid)
            ''')


    @staticmethod
    def row2item(r):
        return {'gid': r[0], 'cid': r[1], 'name': r[2], 'server': r[3]} if r else None


    def add(self, clan):
        with self._connect() as conn:
            try:
                conn.execute('''
                    INSERT INTO {0} ({1}) VALUES (?, ?, ?, ?)
                    '''.format(self._table, self._columns),
                    (clan['gid'], clan['cid'], clan['name'], clan['server']) )
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('ClanDao.add').error(e)
                return -1
            return 0

    
    def delete(self, gid, cid):
        with self._connect() as conn:
            try:
                conn.execute('''
                    DELETE FROM {0} WHERE gid=? AND cid=?
                    '''.format(self._table),
                    (gid, cid) )
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('ClanDao.delete').error(e)
                return -1
            return 0

    
    def modify(self, clan):
        with self._connect() as conn:
            try:
                conn.execute('''
                    UPDATE {0} SET name=?, server=? WHERE gid=? AND cid=?
                    '''.format(self._table),
                    (clan['name'], clan['server'], clan['gid'], clan['cid']) )
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('ClanDao.modify').error(e)
                return -1
            return 0           


    def find_one(self, gid, cid):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE gid=? AND cid=?
                    '''.format(self._table, self._columns),
                    (gid, cid) ).fetchone()
                return self.row2item(ret)
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('ClanDao.find_one').error(e)
            return None


    def find_all(self):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0}
                    '''.format(self._table, self._columns),
                    ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('ClanDao.find_all').error(e)
            return []       


    def find_by_gid(self, gid):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE gid=?
                    '''.format(self._table, self._columns),
                    (gid,) ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('ClanDao.find_by_gid').error(e)
            return []



class MemberDao(SqliteDao):
    def __init__(self):
        super().__init__(
            table='member',
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
        return {'uid': r[0], 'alt': r[1], 'name': r[2], 'gid': r[3], 'cid': r[4]} if r else None


    def add(self, member):
        with self._connect() as conn:
            try:
                conn.execute('''
                    INSERT INTO {0} ({1}) VALUES (?, ?, ?, ?, ?)
                    '''.format(self._table, self._columns),
                    (member['uid'], member['alt'], member['name'], member['gid'], member['cid']) )
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('MemberDao.add').error(e)
                return -1
            return 0

    
    def delete(self, uid, alt):
        with self._connect() as conn:
            try:
                conn.execute('''
                    DELETE FROM {0} WHERE uid=? AND alt=?
                    '''.format(self._table),
                    (uid, alt) )
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('MemberDao.delete').error(e)
                return -1
            return 0


    def modify(self, member):
        with self._connect() as conn:
            try:
                conn.execute('''
                    UPDATE {0} SET name=?, gid=?, cid=? WHERE uid=? AND alt=?
                    '''.format(self._table),
                    (member['name'], member['gid'], member['cid'], member['uid'], member['alt']) )
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('MemberDao.modify').error(e)
                return -1
            return 0           


    def find_one(self, uid, alt):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE uid=? AND alt=?
                    '''.format(self._table, self._columns),
                    (uid, alt) ).fetchone()
                return self.row2item(ret)
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('MemberDao.find_one').error(e)
            return None


    def find_all(self):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0}
                    '''.format(self._table, self._columns),
                    ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('MemberDao.find_all').error(e)
            return []


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
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE {2}
                    '''.format(self._table, self._columns, cond_str), 
                    cond_tup ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('MemberDao.find_by').error(e)
            return []



class BattleDao(SqliteDao):
    NORM    = 0x00
    LAST    = 0x01
    EXT     = 0x02
    TIMEOUT = 0x04

    def __init__(self, gid, cid, yyyy, mm):
        super().__init__(
            table=self.get_table_name(gid, cid, yyyy, mm),
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
            'eid':  r[0], 'uid':   r[1], 'alt':  r[2], 
            'time': r[3], 'round': r[4], 'boss': r[5],
            'dmg':  r[6], 'flag':  r[7] } if r else None


    def add(self, challenge):
        with self._connect() as conn:
            try:
                conn.execute('''
                    INSERT INTO {0} ({1}) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)
                    '''.format(self._table, self._columns),
                    (challenge['uid'], challenge['alt'], challenge['time'], challenge['round'], challenge['boss'], challenge['dmg'], challenge['flag']) )
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('BattleDao.add').error(e)
                return -1
            return 0

    
    def delete(self, eid):
        with self._connect() as conn:
            try:
                conn.execute('''
                    DELETE FROM {0} WHERE eid=?
                    '''.format(self._table),
                    (eid, ) )
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('BattleDao.delete').error(e)
                return -1
            return 0


    def modify(self, challenge):
        with self._connect() as conn:
            try:
                conn.execute('''
                    UPDATE {0} SET uid=?, alt=?, time=?, round=?, boss=?, dmg=?, flag=? WHERE eid=?
                    '''.format(self._table),
                    (challenge['uid'], challenge['alt'], challenge['time'], challenge['round'], challenge['boss'], challenge['dmg'], challenge['flag'], challenge['eid']) )
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('BattleDao.modify').error(e)
                return -1
            return 0


    def find_one(self, eid):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE eid=?
                    '''.format(self._table, self._columns),
                    (eid, ) ).fetchone()
                return self.row2item(ret)
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('BattleDao.find_one').error(e)
            return None


    def find_all(self):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} ORDER BY round, boss, eid
                    '''.format(self._table, self._columns),
                    ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('BattleDao.find_all').error(e)
            return []


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
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE {2} ORDER BY {3}
                    '''.format(self._table, self._columns, cond_str, order), 
                    cond_tup ).fetchall()
                # print('BattleDao.find_by() ret=', ret)
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('BattleDao.find_by').error(e)
            return []


"""
class SubscribeDao(SqliteDao):
    IN_FIGHT  = 0x001
    SUB_BOSS1 = 0x010
    SUB_BOSS2 = 0x020
    SUB_BOSS3 = 0x040
    SUB_BOSS4 = 0x080
    SUB_BOSS5 = 0x100


    def __init__(self):
        super().__init__(
            table='subscribe',
            columns='sid, uid, alt, gid, cid, flag',
            fields='''
            sid INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INT NOT NULL,
            alt INT NOT NULL,
            gid INT NOT NULL,
            cid INT NOT NULL,
            flag INT NOT NULL
            ''')


    @staticmethod
    def row2item(r):
        return {'sid': r[0], 'uid': r[1], 'alt': r[2], 'gid': r[3], 'cid': r[4], 'flag': r[5]} if r else None


    def add(self, subscribe):
        with self._connect() as conn:
            try:
                conn.execute('''
                    INSERT INTO {0} ({1}) VALUES (?, ?, ?, ?, ?, ?)
                    '''.format(self._table, self._columns),
                    (subscribe['sid'], subscribe['uid'], subscribe['alt'], subscribe['gid'], subscribe['cid'], subscribe['flag']) )
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('MemberDao.add').error(e)
                return -1
            return 0

    
    def delete(self, sid):
        with self._connect() as conn:
            try:
                conn.execute('''
                    DELETE FROM {0} WHERE uid=? AND alt=?
                    '''.format(self._table),
                    (uid, alt) )
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('MemberDao.delete').error(e)
                return -1
            return 0


    def modify(self, member):
        with self._connect() as conn:
            try:
                conn.execute('''
                    UPDATE {0} SET name=?, gid=?, cid=? WHERE uid=? AND alt=?
                    '''.format(self._table),
                    (member['name'], member['gid'], member['cid'], member['uid'], member['alt']) )
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('MemberDao.modify').error(e)
                return -1
            return 0           


    def find_one(self, uid, alt):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE uid=? AND alt=?
                    '''.format(self._table, self._columns),
                    (uid, alt) ).fetchone()
                return self.row2item(ret)
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('MemberDao.find_one').error(e)
            return None


    def find_all(self):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0}
                    '''.format(self._table, self._columns),
                    ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('MemberDao.find_all').error(e)
            return []


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
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE {2}
                    '''.format(self._table, self._columns, cond_str), 
                    cond_tup ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logging.getLogger('MemberDao.find_by').error(e)
            return []
"""


