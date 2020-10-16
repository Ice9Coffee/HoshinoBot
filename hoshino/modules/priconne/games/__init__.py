import os
import sqlite3


class Dao:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._create_table()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS win_record "
                "(gid INT NOT NULL, uid INT NOT NULL, count INT NOT NULL, PRIMARY KEY(gid, uid))"
            )

    def get_win_count(self, gid, uid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT count FROM win_record WHERE gid=? AND uid=?", (gid, uid)
            ).fetchone()
            return r[0] if r else 0

    def record_winning(self, gid, uid):
        n = self.get_win_count(gid, uid)
        n += 1
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO win_record (gid, uid, count) VALUES (?, ?, ?)",
                (gid, uid, n),
            )
        return n

    def get_ranking(self, gid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT uid, count FROM win_record WHERE gid=? ORDER BY count DESC LIMIT 10",
                (gid,),
            ).fetchall()
            return r


class GameMaster:
    def __init__(self, db_path):
        self.db_path = db_path
        self.playing = {}

    def is_playing(self, gid):
        return gid in self.playing

    def start_game(self, gid):
        return Game(gid, self)

    def get_game(self, gid):
        return self.playing[gid] if gid in self.playing else None

    @property
    def db(self):
        return Dao(self.db_path)


class Game:
    def __init__(self, gid, game_master):
        self.gid = gid
        self.gm = game_master
        self.answer = 0
        self.winner = 0

    def __enter__(self):
        self.gm.playing[self.gid] = self
        return self

    def __exit__(self, type_, value, trace):
        del self.gm.playing[self.gid]

    def record(self):
        return self.gm.db.record_winning(self.gid, self.winner)


from . import desc_guess
from . import avatar_guess
