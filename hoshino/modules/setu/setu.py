import os
import re
import time
import random

from nonebot import on_command, CommandSession, MessageSegment, NoneBot
from nonebot.exceptions import CQHttpError

from hoshino import R, Service, Privilege
from hoshino.util import FreqLimiter, DailyNumberLimiter

_max = 5
EXCEED_NOTICE = f'您今天已经冲过{_max}次了，请明早5点后再来！'
_nlmt = DailyNumberLimiter(_max)
_flmt = FreqLimiter(5)

sv = Service('setu', manage_priv=Privilege.SUPERUSER, enable_on_default=True, visible=False)
setu_folder = R.img('setu/').path

def setu_gener():
    while True:
        filelist = os.listdir(setu_folder)
        random.shuffle(filelist)
        for filename in filelist:
            if os.path.isfile(os.path.join(setu_folder, filename)):
                yield R.img('setu/', filename).cqcode
                
setu_gener = setu_gener()

def get_setu():
    return setu_gener.__next__()
 

@sv.on_rex(re.compile(r'不够[涩瑟色]|[涩瑟色]图|来一?[点份张].*[涩瑟色]|再来[点份张]|看过了|铜'), normalize=True)
async def setu(bot:NoneBot, ctx, match):
    """随机叫一份涩图，对每个用户有冷却时间"""
    uid = ctx['user_id']    
    if not _nlmt.check(uid):
        await bot.send(ctx, EXCEED_NOTICE, at_sender=True)
        return
    if not _flmt.check(uid):
        await bot.send(ctx, '您冲得太快了，请稍候再冲', at_sender=True)
        return
    _flmt.start_cd(uid)
    _nlmt.increase(uid)

    # conditions all ok, send a setu.
    pic = get_setu()
    try:
        await bot.send(ctx, pic)
    except CQHttpError:
        sv.logger.error(f"发送图片{pic.data['file']}失败")
        try:
            await bot.send(ctx, '涩图太涩，发不出去勒...')
        except:
            pass
