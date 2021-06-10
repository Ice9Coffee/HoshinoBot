# -*- coding: utf-8 -*-

from . import main
from . import utils
from hoshino import R, Service

sv = Service('vortune', visible=True)

@sv.on_rex('抽签|今日人品|今日运势|人品|运势|小狐狸签|吹雪签')
async def entranceFunction(bot, ev):
    msg = str(ev["raw_message"])
    userGroup = ev["group_id"]
    userQQ = ev["user_id"]
    await utils.initialization()
    await main.handlingMessages(msg, bot, userGroup, userQQ, ev)
