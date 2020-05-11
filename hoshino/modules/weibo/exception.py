class WeiboError(Exception):
    def __init__(self, msg, *msgs):
        self._msgs = [msg, *msgs]

    def __str__(self):
        return '\n'.join(self._msgs)

    @property
    def message(self):
        return str(self)

    def append(self, msg:str):
        self._msgs.append(msg)


class ParseError(WeiboError):
    pass


class NotFoundError(WeiboError):
    pass

class DuplicateError(WeiboError):
    pass