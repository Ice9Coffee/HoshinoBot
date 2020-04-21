import os
import re
import random

from hoshino import util
from hoshino.res import R

from . import sv

ship_folder = R.img('kancolle/ship/').path
equip_folder = R.img('kancolle/equip/').path

def _load_data():
    config = util.load_config(__file__)
    db = config.get("data", {})
    rex = re.compile(r"\[CQ:image,file=(.*)\]")
    for k, v in db.items():
        m = rex.search(v)
        if m:
            img = str(R.img('kancolle/', m.group(1)).cqcode)
            db[k] = rex.sub(img, v)
    return db

DB = _load_data()


@sv.on_command('随机舰娘', only_to_me=False)
async def random_ship(session):
    filelist = os.listdir(ship_folder)
    path = None
    while not path or not os.path.isfile(path):
        filename = random.choice(filelist)
        path = os.path.join(ship_folder, filename)
    pic = R.img('kancolle/ship/', filename).cqcode
    await session.send(pic, at_sender=True)


@sv.on_command('随机装备', only_to_me=False)
async def random_equip(session):
    filelist = os.listdir(equip_folder)
    path = None
    while not path or not os.path.isfile(path):
        filename = random.choice(filelist)
        path = os.path.join(equip_folder, filename)
    pic = R.img('kancolle/equip/', filename).cqcode
    await session.send(pic, at_sender=True)


@sv.on_rex(r"^\*", normalize=False)
async def kc_query(bot, ctx, m):
    key = ctx['message'].extract_plain_text()
    if key in DB:
        sv.logger.info(DB[key])
        await bot.send(ctx, DB[key], at_sender=True)
