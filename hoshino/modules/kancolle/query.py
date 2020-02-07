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

sv = Service('kc-query', enable_on_default=False)

ship_folder = R.img('kancolle/ship/').path
equip_folder = R.img('kancolle/equip/').path

@sv.on_command('随机舰娘', only_to_me=False)
async def random_ship(session:CommandSession):
    filelist = os.listdir(ship_folder)
    path = None
    while not path or not os.path.isfile(path):
        filename = random.choice(filelist)
        path = os.path.join(ship_folder, filename)
    pic = R.img('kancolle/ship/', filename).cqcode
    await session.send(pic, at_sender=True)


@sv.on_command('随机装备', only_to_me=False)
async def random_equip(session:CommandSession):
    filelist = os.listdir(equip_folder)
    path = None
    while not path or not os.path.isfile(path):
        filename = random.choice(filelist)
        path = os.path.join(equip_folder, filename)
    pic = R.img('kancolle/equip/', filename).cqcode
    await session.send(pic, at_sender=True)
