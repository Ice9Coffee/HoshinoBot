# 公主连接Re:Dive会战管理插件
# clan == クラン == 戰隊（直译为氏族）（CLANNAD的CLAN（笑））

import re
from typing import Callable, Dict, Tuple, Iterable

from nonebot import NoneBot
from hoshino import util
from hoshino.service import Service, Privilege
from .argparse import ArgParser
from .exception import *

sv = Service('clanbattle', manage_priv=Privilege.SUPERUSER, enable_on_default=False)
SORRY = 'ごめんなさい！嘤嘤嘤(〒︿〒)'


_registry:Dict[str, Tuple[Callable, ArgParser]] = {}


@sv.on_rex(re.compile(r'^[!！](.+)', re.DOTALL), event='group')
async def _clanbattle_bus(bot:NoneBot, ctx, match):
    cmd, *args = match.group(1).split()
    cmd = util.normalize_str(cmd)
    if cmd in _registry:
        func, parser = _registry[cmd]
        try:
            args = parser.parse(args, ctx['message'])
            await func(bot, ctx, args)
        except DatabaseError as e:
            await bot.send(ctx, f"DatabaseError: {e.message}\n{SORRY}\n※请及时联系维护组")
        except ClanBattleError as e:
            await bot.send(ctx, e.message, at_sender=True)
        except Exception as e:
            sv.logger.exception(e)
            sv.logger.error(f'{type(e)} occured when {func.__name__} handling message {ctx["message_id"]}.')
            await bot.send(ctx, 'Error: 机器人出现未预料的错误\n{SORRY}\n※请及时联系维护组', at_sender=True)


def cb_cmd(name, parser:ArgParser) -> Callable:
    name = util.normalize_str(name)
    def _(func) -> Callable:
        if isinstance(name, str):
            name = (name, )
        if not isinstance(name, Iterable):
            raise ValueError('`name` of cb_cmd must be `str` or `Iterable[str]`')
        names = map(lambda x: util.normalize_str(x), name)
        for n in names:
            if n in _registry:
                sv.logger.warning(f'出现重名命令：{func.__name__} 与 {_registry[n].__name__}命令名冲突')
            else:
                _registry[n] = (func, parser)
        return func


from .cmdv1 import *
from .cmdv2 import *
