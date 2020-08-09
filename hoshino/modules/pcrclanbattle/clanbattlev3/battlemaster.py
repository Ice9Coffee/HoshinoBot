import os
import sqlite3
from datetime import datetime, timedelta, timezone
from .model import *

DB_FOLDER = os.path.expanduser('~/.hoshino/clanbattlev3/')
os.makedirs(DB_FOLDER, exist_ok=True)


def get_yyyymmdd(time, zone_num:int=8):
    '''返回time对应的会战年月日。
    
    其中，年月为该期会战的年月；日为刷新周期对应的日期。
    会战为每月最后一星期，编程时认为mm月的会战一定在mm月20日至mm+1月10日之间，每日以5:00 UTC+8为界。
    注意：返回的年月日并不一定是自然时间，如2019年9月2日04:00:00我们认为对应2019年8月会战，日期仍为1号，将返回(2019,8,1)
    '''
    # 日台服均为当地时间凌晨5点更新，故减5
    time = time.astimezone(timezone(timedelta(hours=zone_num - 5)))
    yyyy = time.year
    mm = time.month
    dd = time.day
    if dd < 20:
        mm = mm - 1
    if mm < 1:
        mm = 12
        yyyy = yyyy - 1
    return (yyyy, mm, dd)


class BattleMaster:
    def __init__(self, gid, time):
        self.gid = gid
        self.yyyy, self.mm, _ = get_yyyymmdd(time)
        self._create_tables()


    def _connect_clan_db(self):
        db = os.path.join(DB_FOLDER, 'clan.db')
        return sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)


    def _connect_battle_db(self):
        db = os.path.join(DB_FOLDER, f'battle{self.yyyy:04d}{self.mm:02d}.db')
        return sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)


    def _create_tables(self):
        with self._connect_clan_db() as conn:
            sql = "CREATE TABLE IF NOT EXISTS clan" \
                  "(gid INT PRIMARY KEY NOT NULL, name TEXT NOT NULL, server INT NOT NULL)"
            conn.execute(sql)
            sql = "CREATE TABLE IF NOT EXISTS member" \
                  "(gid INT NOT NULL, uid INT NOT NULL, name TEXT NOT NULL, PRIMARY KEY (gid, uid))"
            conn.execute(sql)
        
        with self._connect_battle_db() as conn:
            sql = f"CREATE TABLE IF NOT EXISTS challenge_{self.gid}" \
                   "(eid INTEGER PRIMARY KEY AUTOINCREMENT, uid INT NOT NULL, time DATETIME NOT NULL, round INT NOT NULL, boss INT NOT NULL, dmg INT NOT NULL, flag INT NOT NULL)"
            conn.execute(sql)
            sql = "CREATE TABLE IF NOT EXISTS progress" \
                  "(gid INT PRIMARY KEY NOT NULL, round INT NOT NULL, boss INT NOT NULL, hp INT NOT NULL)"
            conn.execute(sql)
            sql = "CREATE TABLE IF NOT EXISTS pause" \
                  "(gid INT NOT NULL, uid INT NOT NULL, dmg INT NOT NULL, second_left INT NOT NULL)"
            conn.execute(sql)
            sql = "CREATE TABLE IF NOT EXISTS sos" \
                  "(gid INT NOT NULL, uid INT NOT NULL, time DATETIME NOT NULL, round INT NOT NULL, boss INT NOT NULL)"
            conn.execute(sql)
            sql = "CREATE TABLE IF NOT EXISTS sl" \
                  "(gid INT NOT NULL, uid INT NOT NULL, time DATETIME NOT NULL, round INT NOT NULL, boss INT NOT NULL)"
            conn.execute(sql)
            sql = "CREATE TABLE IF NOT EXISTS subscribe" \
                  "(gid INT NOT NULL, uid INT NOT NULL, time DATETIME NOT NULL, round INT NOT NULL, boss INT NOT NULL)"
            conn.execute(sql)
            
            
    def get_clan(self):
        with self._connect_clan_db() as conn:
            clan = conn.execute("SELECT gid, name, server FROM clan WHERE gid=?", 
                                (self.gid, )).fetchone()
            return Clan(*clan) if clan else None
    
    
    def add_clan(self, clan: Clan):
        with self._connect_clan_db() as conn:
            conn.execute("INSERT OR REPLACE INTO clan (gid, name, server) VALUES (?, ?, ?)",
                         (clan.gid, clan.name, clan.server))
    
    
    def get_member(self, uid):
        with self._connect_clan_db() as conn:
            m = conn.execute("SELECT uid, gid, name FROM member WHERE gid=? and uid=?",
                             (self.gid, uid)).fetchone()
            return Member(*m) if m else None
    
    
    def add_member(self, member: Member):
        with self._connect_clan_db() as conn:
            conn.execute("INSERT OR REPLACE INTO member (uid, gid, name) VALUES (?, ?, ?)",
                         (member.uid, member.gid, member.name))
    
    
    def del_member(self, uid):
        with self._connect_clan_db() as conn:
            conn.execute("DELETE FROM member WHERE uid=?", (uid, ))

    
            
            