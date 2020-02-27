import os
import re
import random

from nonebot import on_command, CommandSession, NoneBot
from hoshino import util
from hoshino.res import R
from hoshino.service import Service

sv = Service('kc-query', enable_on_default=False)

ship_folder = R.img('kancolle/ship/').path
equip_folder = R.img('kancolle/equip/').path

def load_data():
    config = util.load_config(__file__)
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


@sv.on_rex(re.compile(r"^\*"), normalize=False, event='group')
async def kc_query(bot:NoneBot, ctx, m):
    key = ctx['message'].extract_plain_text()
    if key in DB:
        sv.logger.info(DB[key])
        await bot.send(ctx, DB[key], at_sender=True)
