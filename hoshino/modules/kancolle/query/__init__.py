from hoshino.service import Service

import os
import re
import time
import random
import ujson as json
from collections import defaultdict
from urllib.parse import quote

from nonebot import on_command, CommandSession, MessageSegment, NoneBot
from nonebot.exceptions import CQHttpError

from hoshino.res import R
from hoshino.util import silence
from hoshino.service import Service, Privilege

sv = Service('kc-query', enable_on_default=False)

ship_folder = R.img('kancolle/ship/').path
equip_folder = R.img('kancolle/equip/').path

def load_data():
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_file, encoding='utf8') as f:
        config = json.load(f)
        db = config["data"]
        rex = re.compile(r"\[CQ:image,file=(.*)\]")
        for k, v in db.items():
            m = rex.search(v)
            if m:
                img = str(R.img('kancolle/', m.group(1)).cqcode)
                db[k] = rex.sub(img, v)
        return db

DB = load_data()


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


@sv.on_rex(re.compile(r"^\*"))
async def kc_query(bot:NoneBot, ctx, m):
    key = ctx['message'].extract_plain_text()
    if key in DB:
        sv.logger.info(DB[key])
        await bot.send(ctx, DB[key], at_sender=True)
