from typing import Any, Union, Callable
from aiocqhttp.typing import Message_T
from hoshino import logger
from nonebot.message import CanceledException
import nonebot
from hoshino.typing import CQEvent as Event
from datetime import datetime, timedelta
from collections import defaultdict

_allsession = {}
_allaction = defaultdict(dict)


class ActSession:
    def __init__(self, name: str, group_id: int, user_id: int, max_user: int, expire_time: int, usernum_limit: bool):
        self.name = name
        self.bot = nonebot.get_bot()
        self.group_id = group_id  # session所在群聊
        self.creator = user_id  # session的创建者
        self.usernum_limit = usernum_limit
        self.users = list([user_id])
        self.max_user = max_user
        self.is_valid = True
        self.last_interaction = None
        self.expire_time = expire_time
        self.create_time = datetime.now()
        self._state = {}
        self._actions = {}
        # self.handle_msg = None

    def __getattr__(self, item) -> Any:
        return self.state.get(item)

    @property
    def state(self):
        """
        State of the session.

        This contains all named arguments and
        other session scope temporary values.
        """
        return self._state

    @property
    def actions(self):
        """
        Actions of the session.

        This dict contains all actions which
        can be triggered by certain word
        """
        return _allaction.get(self.name) or {}

    @property
    def handle_msg(self) -> Callable:
        return interact.allhandler.get(self.name)

    @classmethod
    def from_event(cls, name: str, event: Event, max_user: int = 100, expire_time: int = 300,
                   usernum_limit: bool = False):
        return cls(name, event.group_id, event.user_id, max_user, expire_time, usernum_limit)

    def count_user(self) -> int:
        return len(self.users)

    def add_user(self, uid: int):
        # this function should cautiously be used
        # because it can not assure user add only one session in the same group
        # better to use join_session in InteractHandler
        if len(self.users) >= self.max_user:
            raise ValueError('人数超过限制,无法加入')
        self.users.append(uid)

    def close(self, message: Message_T = None):
        InteractHandler().close_session(self.group_id, self.name)
        logger.info(f'interaction session {self.name} has been closed')

    def is_expire(self) -> bool:
        now = datetime.now()
        return self.create_time + timedelta(seconds=self.expire_time) < now

    async def send(self, event, message, **kwargs):
        await self.bot.send(event, message, **kwargs)

    async def finish(self, event, message, **kwargs):
        await self.send(event, message, **kwargs)
        raise CanceledException('finished')


class InteractHandler:
    def __init__(self) -> None:
        self.allsession = {}
        global _allaction
        global _allsession
        # global _allhandler
        self.allsession = _allsession
        self.allaction = _allaction
        self.allhandler = {}

    def add_session(self, session: ActSession):
        gid = session.group_id
        name = session.name
        if (gid, name) in self.allsession:
            raise ValueError(f'{self.allsession[(gid, name)].name} 正在进行中')
        self.allsession[(gid, name)] = session

    @staticmethod
    def close_session(group_id: int, name: str):
        global _allsession
        if (group_id, name) in _allsession:
            del _allsession[(group_id, name)]

    def find_session(self, event: Event, name=None) -> ActSession:
        gid = event.group_id
        uid = event.user_id
        if name:  # 指定名称直接获取
            return self.allsession.get((gid, name))
        for k in self.allsession:
            if gid == k[0]:
                if not self.allsession[k].usernum_limit or uid in self.allsession[k].users:
                    return self.allsession[k]
        return None

    def add_action(self, name: str, trigger_word: Union[str, set]):
        """
        用作装饰器
        """
        if isinstance(trigger_word, str):
            trigger_word = (trigger_word,)

        def deco(func: Callable) -> Callable:
            for tw in trigger_word:
                if tw in self.allaction[name]:
                    raise ValueError('action trigger word duplication')
                self.allaction[name][tw] = func

        return deco

    def add_msg_handler(self, session_name: str):
        """
        用作装饰器
        """

        def deco(func: Callable) -> Callable:
            self.allhandler[session_name] = func

        return deco

    def join_session(self, event: Event, session: ActSession):
        ssn = self.find_session(event)
        if ssn:  # user已经在此session或者其它session中
            raise ValueError(f'已经在{ssn.name}中，无法再次加入或者加入其它互动')
        ssn = session
        ssn.add_user(event.user_id)


interact = InteractHandler()
