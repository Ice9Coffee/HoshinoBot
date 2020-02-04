import os
import re
import time
import random
from collections import defaultdict

from nonebot import on_command, CommandSession, MessageSegment, NoneBot
from nonebot.exceptions import CQHttpError

from hoshino.res import R
from hoshino.util import silence
from hoshino.service import Service, Privilege


sv = Service('kc-ship', enable_on_default=False)

ship_folder = R.img('ship/').path

def get_ship():
    try:
        path = None
        filename = None
        filelist = os.listdir(ship_folder)
        filelist = sorted(filelist, key=lambda x: os.path.getmtime(os.path.join(ship_folder, x)), reverse=True)
        while not path or not os.path.isfile(path):
            i = round(random.expovariate(0.02))  # 期望为 1 / λ
            i = random.randint(0, len(filelist) - 1) if i >= len(filelist) else i
            filename = filelist[i]
            path = os.path.join(ship_folder, filename)
        return R.img('ship/', filename).cqcode
    except Exception as e:
        sv.logger.exception(e)
        sv.logger.exception(f'f={filename}, x={path}')
        return MessageSegment.text('Error: 挑选涩图时发生异常')


@sv.on_rex(re.compile(r'随机舰娘'))
async def setu(bot:NoneBot, ctx, match):
    filelist = os.listdir(ship_folder)
    path = None
    while not path or not os.path.isfile(path):
        filename = random.choice(filelist)
        path = os.path.join(ship_folder, filename)
    pic = R.img('ship/', filename).cqcode
    await bot.send(ctx, pic, at_sender=True)
