from .model import *


class BaseTable:
    def create(self, conn):
        raise NotImplementedError

    def add(self, conn, obj):
        raise NotImplementedError

    def get(self, conn, idx):
        raise NotImplementedError

    def remove(self, conn, idx):
        raise NotImplementedError


class ClanTable(BaseTable):
    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS clan "
            "(gid INT PRIMARY KEY NOT NULL, name TEXT NOT NULL, server INT NOT NULL)"
        )

    def add(self, conn, clan: Clan):
        conn.execute(
            "INSERT OR REPLACE INTO clan (gid, name, server) VALUES (?, ?, ?)",
            (clan.gid, clan.name, clan.server),
        )

    def get(self, conn, gid):
        x = conn.execute(
            "SELECT gid, name, server FROM clan WHERE gid=?", (gid,)
        ).fetchone()
        return Clan(*x) if x else None

    def remove(self, conn, gid):
        conn.execute("DELETE FROM clan WHERE gid=?", (gid,))


class MemberTable(BaseTable):
    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS member "
            "(gid INT NOT NULL, uid INT NOT NULL, name TEXT NOT NULL, "
            "PRIMARY KEY (gid, uid))"
        )

    def add(self, conn, member: Member):
        conn.execute(
            "INSERT OR REPLACE INTO member (gid, uid, name) VALUES (?, ?, ?)",
            (member.gid, member.uid, member.name),
        )

    def get(self, conn, guid):
        x = conn.execute(
            "SELECT uid, gid, name FROM member WHERE gid=? AND uid=?", guid
        ).fetchone()
        return Member(*x) if x else None

    def remove(self, conn, guid):
        conn.execute("DELETE FROM member WHERE gid=? AND uid=?", guid)


class ChallengeTable(BaseTable):
    def __init__(self, gid):
        self.gid = gid

    @property
    def table_name(self):
        return f"challenge_{self.gid}"

    def create(self, conn):
        conn.execute(
            f"CREATE TABLE IF NOT EXISTS {self.table_name} "
            "(eid INTEGER PRIMARY KEY AUTOINCREMENT, uid INT NOT NULL, "
            "time DATETIME NOT NULL, round INT NOT NULL, boss INT NOT NULL, "
            "dmg INT NOT NULL, flag INT NOT NULL)"
        )

    def add(self, conn, ch: Challenge):
        cur = conn.execute(
            f"INSERT OR REPLACE INTO {self.table_name} "
            "(uid, time, round, boss, dmg, flag) VALUES (?, ?, ?, ?, ?, ?)",
            (ch.uid, ch.time, ch.round, ch.boss, ch.dmg, ch.flag),
        )
        ch.eid = cur.lastrowid

    def remove(self, conn, eid):
        conn.execute(f"DELETE FROM {self.table_name} WHERE eid=?", (eid,))

    def get_latest_flag(self, conn, uid):
        x = conn.execute(
            f"SELECT flag FROM {self.table_name} WHERE uid=? ORDER BY round DESC, boss DESC, time DESC",
            (uid,),
        ).fetchone()
        return x[0] if x else 0


class ProgressTable(BaseTable):
    def __init__(self, gid):
        self.gid = gid

    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS progress "
            "(gid INT PRIMARY KEY NOT NULL, round INT NOT NULL, "
            "boss INT NOT NULL, hp INT NOT NULL)"
        )

    def add(self, conn, progress: Progress):
        conn.execute(
            "INSERT OR REPLACE INTO progress "
            "(gid, round, boss, hp) VALUES (?, ?, ?, ?)",
            (self.gid, progress.round, progress.boss, progress.hp),
        )

    def get(self, conn, gid=None):
        x = conn.execute(
            "SELECT round, boss, hp FROM progress WHERE gid=?", (gid or self.gid,)
        ).fetchone()
        return (
            Progress(*x) if x else Progress(1, 1, 6000000)
        )  # FIXME: hp of r1b1 may change?


class PauseTable(BaseTable):
    def __init__(self, gid):
        self.gid = gid

    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS pause"
            "(gid INT NOT NULL, uid INT NOT NULL, dmg INT NOT NULL, second_left INT NOT NULL, "
            "PRIMARY KEY (gid, uid))"
        )

    def add(self, conn, pause: PauseRecord):
        conn.execute(
            "INSERT OR REPLACE INTO pause (gid, uid, dmg, second_left) VALUES (?, ?, ?, ?)",
            (self.gid, pause.uid, pause.dmg, pause.second_left),
        )

    def count(self, conn):
        x = conn.execute(
            "SELECT COUNT(*) FROM pause WHERE gid=?", (self.gid,)
        ).fetchone()
        return x[0]

    def remove(self, conn, uid):
        conn.execute("DELETE FROM pause WHERE gid=? AND uid=?", (self.gid, uid))

    def clear(self, conn):
        conn.execute("DELETE FROM pause WHERE gid=?", (self.gid,))

    def list(self, conn):
        xx = conn.execute(
            "SELECT uid, dmg, second_left FROM pause WHERE gid=? ORDER BY dmg DESC",
            (self.gid,),
        ).fetchall()
        return [PauseRecord(*x) for x in xx]


class SosTable(BaseTable):
    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS sos"
            "(gid INT NOT NULL, uid INT NOT NULL, time DATETIME NOT NULL, "
            "round INT NOT NULL, boss INT NOT NULL)"
        )


class SlTable(BaseTable):
    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS sl"
            "(gid INT NOT NULL, uid INT NOT NULL, time DATETIME NOT NULL, "
            "round INT NOT NULL, boss INT NOT NULL)"
        )


class SubrTable(BaseTable):
    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS subscribe"
            "(gid INT NOT NULL, uid INT NOT NULL, time DATETIME NOT NULL, "
            "round INT NOT NULL, boss INT NOT NULL)"
        )
