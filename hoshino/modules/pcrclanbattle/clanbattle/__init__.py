# 公主连接Re:Dive会战管理插件
# clan == クラン == 戰隊（直译为氏族）（CLANNAD的CLAN（笑））

from typing import Callable, Dict, Tuple, Iterable

from nonebot import NoneBot, on_command, CommandSession
from hoshino import util
from hoshino.service import Service, Privilege
from hoshino.res import R
from .argparse import ArgParser
from .exception import *

sv = Service('clanbattle', manage_priv=Privilege.SUPERUSER, enable_on_default=True)
SORRY = 'ごめんなさい！嘤嘤嘤(〒︿〒)'

_registry:Dict[str, Tuple[Callable, ArgParser]] = {}

@sv.on_message('group')
async def _clanbattle_bus(bot:NoneBot, ctx):
    # check prefix
    start = ''
    for m in ctx['message']:
        if m.type == 'text':
            start = m.data.get('text', '').lstrip()
            break
    if not start or start[0] not in '!！':
        return

    # find cmd
    plain_text = ctx['message'].extract_plain_text()
    cmd, *args = plain_text.split()
    cmd = util.normalize_str(cmd[1:])
    if cmd in _registry:
        func, parser = _registry[cmd]
        try:
            sv.logger.info(f'Message {ctx["message_id"]} is a clanbattle command, start to process by {func.__name__}.')
            args = parser.parse(args, ctx['message'])
            await func(bot, ctx, args)
            sv.logger.info(f'Message {ctx["message_id"]} is a clanbattle command, handled by {func.__name__}.')
        except DatabaseError as e:
            await bot.send(ctx, f'DatabaseError: {e.message}\n{SORRY}\n※请及时联系维护组', at_sender=True)
        except ClanBattleError as e:
            await bot.send(ctx, e.message, at_sender=True)
        except Exception as e:
            sv.logger.exception(e)
            sv.logger.error(f'{type(e)} occured when {func.__name__} handling message {ctx["message_id"]}.')
            await bot.send(ctx, f'Error: 机器人出现未预料的错误\n{SORRY}\n※请及时联系维护组', at_sender=True)


def cb_cmd(name, parser:ArgParser) -> Callable:
    if isinstance(name, str):
        name = (name, )
    if not isinstance(name, Iterable):
        raise ValueError('`name` of cb_cmd must be `str` or `Iterable[str]`')
    names = map(lambda x: util.normalize_str(x), name)
    def deco(func) -> Callable:
        for n in names:
            if n in _registry:
                sv.logger.warning(f'出现重名命令：{func.__name__} 与 {_registry[n].__name__}命令名冲突')
            else:
                _registry[n] = (func, parser)
        return func
    return deco


# from .cmdv1 import *
from .cmdv2 import *


QUICK_START = f'''
======================
- Hoshino会战管理v2.0 -
======================
快速开始指南
【必读事项】
※会战系命令均以感叹号!开头，半全角均可
※命令与参数之间必须以【空格】隔开
※下面以使用场景-使用例给出常用指令的说明
【群初次使用】
!建会 N自警団（カォン） Sjp
!建会 N哞哞自衛隊 Stw
!建会 N自卫团 Scn
【注册成员】
!入会 祐树
!入会 佐树 @123456789
【上报伤害】
!出刀 514w
!收尾
!补时刀 114w
【预约Boss】
!预约 5 M留言
!取消预约 5
【锁定Boss】
!锁定
!解锁
【查询余刀&催刀】
!查刀
!催刀

※前往 t.cn/A6wBzowv 查看完整命令一览表
※如有问题请先阅读一览表底部的FAQ
※使用前请务必【逐字】阅读开头的必读事项
'''.rstrip()

@on_command('!帮助', aliases=('！帮助', '!幫助', '！幫助', '!help', '！help'), only_to_me=False)
async def cb_help(session:CommandSession):
    await session.send(QUICK_START, at_sender=True)
