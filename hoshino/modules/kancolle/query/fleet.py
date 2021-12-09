import os
import re
import random

from hoshino import util, R

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


@sv.on_fullmatch('随机舰娘')
async def random_ship(bot, ev):
    filelist = os.listdir(ship_folder)
    path = None
    while not path or not os.path.isfile(path):
        filename = random.choice(filelist)
        path = os.path.join(ship_folder, filename)
    pic = R.img('kancolle/ship/', filename).cqcode
    await bot.send(ev, pic, at_sender=True)


@sv.on_fullmatch('随机装备')
async def random_equip(bot, ev):
    filelist = os.listdir(equip_folder)
    path = None
    while not path or not os.path.isfile(path):
        filename = random.choice(filelist)
        path = os.path.join(equip_folder, filename)
    pic = R.img('kancolle/equip/', filename).cqcode
    await bot.send(ev, pic, at_sender=True)


@sv.on_prefix('*')
async def kc_query(bot, ev):
    key = ev.message.extract_plain_text()
    if key in DB:
        sv.logger.info(DB[key])
        await bot.send(ev, DB[key], at_sender=True)
    else:
        sv.logger.info(f"{key} not found!")
