import os
import re
import time
import random
from collections import defaultdict

from nonebot import on_command, CommandSession, MessageSegment, NoneBot
from nonebot import permission as perm

from hoshino.res import R
from hoshino.util import silence
from hoshino.service import Service, Privilege


sv = Service('setu', manage_priv=Privilege.SUPERUSER, enable_on_default=False)

setu_folder = R.img('setu/').path
last_call_time = defaultdict(int)   # user_id: t in seconds
cd_time = 5    # in seconds



def get_setu():
    try:
        x = None
        f = None
        while not x or not os.path.isfile(x):
            f = random.choice(os.listdir(setu_folder))
            x = os.path.join(setu_folder, f)
        return R.img('setu/', f).cqcode
    except Exception as e:
        sv.logger.exception(e)
        sv.logger.exception(f'f={f}, x={x}')
        return MessageSegment.text('Error: 挑选涩图时发生异常')


@sv.on_rex(re.compile(r'铜|不够[涩色]|[涩色]图|来一?[点份张]'), 'group')
async def setu(bot:NoneBot, ctx, match):
    """
    随机叫一份涩图，对每个用户有冷却时间
    """
    now = time.time()
    if now > (last_call_time[ctx['user_id']] + cd_time):
        last_call_time[ctx['user_id']] = now
        await bot.send(ctx, get_setu())
    else:
        await bot.send(ctx, '您冲得太快了，请稍候再冲', at_sender=True)
