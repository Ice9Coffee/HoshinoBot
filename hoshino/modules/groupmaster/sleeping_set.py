import re
import math
import random

import nonebot
from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession
from nonebot import permission as perm

from hoshino.util import silence


@on_command('sleep_8h', aliases=('睡眠套餐', '休眠套餐', '精致睡眠', '来一份精致睡眠套餐', '精緻睡眠', '來一份精緻睡眠套餐'), permission=perm.GROUP) 
async def sleep_8h(session: CommandSession):
    await silence(session.ctx, 8*60*60, ignore_super_user=True)


@on_natural_language(keywords={'套餐'}, permission=perm.GROUP, only_to_me=False)
async def sleep(session:NLPSession):
    arg = session.msg_text.strip()
    rex = re.compile(r'(来|來)(.*(份|个)(.*)(睡|茶)(.*))套餐')
    base = 0 if '午' in arg else 5*60*60
    m = rex.search(arg)
    if m:
        length = len(m.group(1))
        sleep_time = base + round(math.sqrt(length) * 60 * 30 + 60 * random.randint(-15, 15))
        await silence(session.ctx, sleep_time, ignore_super_user=True)
