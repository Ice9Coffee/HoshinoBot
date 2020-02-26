import os
import re
import time
import pytz
import random
from datetime import datetime, timedelta
from collections import defaultdict

from nonebot import on_command, CommandSession, MessageSegment, NoneBot
from nonebot.exceptions import CQHttpError

from hoshino.res import R
from hoshino.util import silence
from hoshino.service import Service, Privilege


sv = Service('setu', manage_priv=Privilege.SUPERUSER, enable_on_default=False, visible=False)
_last_setu_day = -1
_user_setu_count = defaultdict(int)    # {user: gacha_count}
_max_setu_per_day = 5
SETU_EXCEED_NOTICE = f'您今天已经冲过{_max_setu_per_day}次了，请明天再来！'

setu_folder = R.img('setu/').path
last_call_time = defaultdict(int)   # user_id: t in seconds
cd_time = 5    # in seconds

def check_setu_num(user_id):
    global _last_setu_day, _user_setu_count
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    day = (now - timedelta(hours=5)).day
    if day != _last_setu_day:
        _last_setu_day = day
        _user_setu_count.clear()
    return bool(_user_setu_count[user_id] < _max_setu_per_day)


def get_setu():
    try:
        path = None
        filename = None
        filelist = os.listdir(setu_folder)
        filelist = sorted(filelist, key=lambda x: os.path.getmtime(os.path.join(setu_folder, x)), reverse=True)
        while not path or not os.path.isfile(path):
            # i = round(random.expovariate(0.02))  # 期望为 1 / λ
            i = random.randint(0, len(filelist) - 1) # if i >= len(filelist) else i
            filename = filelist[i]
            path = os.path.join(setu_folder, filename)
        return R.img('setu/', filename).cqcode
    except Exception as e:
        sv.logger.exception(e)
        sv.logger.exception(f'f={filename}, x={path}')
        return MessageSegment.text('Error: 挑选涩图时发生异常')


@sv.on_rex(re.compile(r'不够[涩瑟色]|[涩瑟色]图|来一?[点份张].*[涩瑟色]|再来[点份张]|看过了|铜'), normalize=True, event='group')
async def setu(bot:NoneBot, ctx, match):
    """随机叫一份涩图，对每个用户有冷却时间"""
    
    uid = ctx['user_id']
    now = time.time()
    
    if now < (last_call_time[uid] + cd_time):
        await bot.send(ctx, '您冲得太快了，请稍候再冲', at_sender=True)
        return
    last_call_time[uid] = now
    
    if not check_setu_num(uid):
        await bot.send(ctx, SETU_EXCEED_NOTICE, at_sender=True)
        return
    _user_setu_count[uid] += 1

    # conditions all ok, send a setu.
    try:
        await bot.send(ctx, get_setu())
    except CQHttpError:
        await bot.send(ctx, '涩图太涩，发不出去勒...')
