import re
import random

from hoshino import Service
from hoshino.typing import CQEvent
from hoshino.util import filt_message

sv = Service('dice', help_='''
[.r] 掷骰子
[.r 3d12] 掷3次12面骰子
'''.strip())

async def do_dice(bot, ev, num, min_, max_, opr, offset, TIP="的掷骰结果是："):
    if num == 0:
        await bot.send(ev, '咦？我骰子呢？')
        return
    min_, max_ = min(min_, max_), max(min_, max_)
    rolls = list(map(lambda _: random.randint(min_, max_), range(num)))
    sum_ = sum(rolls)
    rolls_str = '+'.join(map(lambda x: str(x), rolls))
    if len(rolls_str) > 100:
        rolls_str = str(sum_)
    res = sum_ + opr * offset
    msg = [
        f'{TIP}\n', str(num) if num > 1 else '', 'D',
        f'{min_}~' if min_ != 1 else '', str(max_),
        (' +-'[opr] + str(offset)) if offset else '',
        '=', rolls_str, (' +-'[opr] + str(offset)) if offset else '',
        f'={res}' if offset or num > 1 else '',
    ]
    msg = ''.join(msg)
    await bot.send(ev, msg, at_sender=True)


@sv.on_rex(re.compile(r'^\.r\s*((?P<num>\d{0,2})d((?P<min>\d{1,4})~)?(?P<max>\d{0,4})((?P<opr>[+-])(?P<offset>\d{0,5}))?)?\b', re.I))
async def dice(bot, ev):
    num, min_, max_, opr, offset = 1, 1, 100, 1, 0
    match = ev['match']
    if s := match.group('num'):
        num = int(s)
    if s := match.group('min'):
        min_ = int(s)
    if s := match.group('max'):
        max_ = int(s)
    if s := match.group('opr'):
        opr = -1 if s == '-' else 1
    if s := match.group('offset'):
        offset = int(s)
    await do_dice(bot, ev, num, min_, max_, opr, offset)


@sv.on_prefix('.qj')
async def kc_marriage(bot, ev: CQEvent):
    wife = filt_message(ev.message.extract_plain_text().strip())
    tip = f'与{wife}的ケッコンカッコカリ结果是：' if wife else '的ケッコンカッコカリ结果是：'
    await do_dice(bot, ev, 1, 3, 6, 1, 0, tip)
