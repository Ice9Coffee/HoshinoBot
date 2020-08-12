import sqlite3


class ClanBattleError(Exception):
    def __init__(self, *msgs):
        self.msg = msgs if msgs else []

    def __str__(self):
        return "\n".join(self.msg)

    @property
    def message(self):
        return str(self)

    def append(self, msg: str):
        self.msg.append(msg)


class ParseError(ClanBattleError):
    pass


class NotFoundError(ClanBattleError):
    pass


class AlreadyExistError(ClanBattleError):
    pass


class PermissionDeniedError(ClanBattleError):
    pass


class DatabaseError(ClanBattleError, sqlite3.DatabaseError):
    pass
