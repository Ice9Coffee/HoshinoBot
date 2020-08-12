import os
import sqlite3
from datetime import datetime
from . import helper
from .table import *

DB_FOLDER = os.path.expanduser("~/.hoshino/clanbattlev3/")
os.makedirs(DB_FOLDER, exist_ok=True)


class BattleMaster:
    def __init__(self, gid, time=None):
        self.gid = gid
        self.year, self.month, _ = helper.yyyymmdd(time or datetime.now())
        self.clan = ClanTable()
        self.member = MemberTable()
        self.challenge = ChallengeTable(gid)
        self.progress = ProgressTable(gid)
        self.pause = PauseTable(gid)
        self.sos = SosTable()
        self.sl = SlTable()
        self.subr = SubrTable()
        self._create_tables()

    def connect_clan_db(self):
        db = os.path.join(DB_FOLDER, "clan.db")
        return sqlite3.connect(
            db, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )

    def connect_battle_db(self):
        db = os.path.join(DB_FOLDER, f"battle{self.year:04d}{self.month:02d}.db")
        return sqlite3.connect(
            db, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )

    def _create_tables(self):
        with self.connect_clan_db() as conn:
            self.clan.create(conn)
            self.member.create(conn)

        with self.connect_battle_db() as conn:
            self.challenge.create(conn)
            self.progress.create(conn)
            self.pause.create(conn)
            self.sos.create(conn)
            self.sl.create(conn)
            self.subr.create(conn)

    def uid2name(self, conn, uids):
        names = []
        for uid in uids:
            x = conn.execute(
                "SELECT name FROM member WHERE gid=? AND uid=?", (self.gid, uid)
            ).fetchone()
            names.append(x[0] if x else str(uid))
        return names
