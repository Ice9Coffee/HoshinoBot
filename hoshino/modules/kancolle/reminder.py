import os
import pytz
import random
import ujson as json
from datetime import datetime

import nonebot

from hoshino.service import Service

sv = Service('kc-reminder', enable_on_default=False)

@sv.scheduled_job('cron', hour='13', minute='30')
async def enshu_reminder():
    msgs = [
        '演习即将刷新！\n莫让下午的自己埋怨上午的自己：\n「演習」で練度向上！0/3',
        '[CQ:at,qq=all] 演习即将刷新！',
    ]
    await sv.broad_cast(msgs, 'enshu_reminder', 0)


@sv.scheduled_job('cron', day='12-14', hour='22')
async def ensei_reminder():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    remain_days = 15 - now.day
    msgs = [
        f'【远征提醒小助手】提醒您月常远征还有{remain_days}天刷新！',
        f'[CQ:at,qq=all] 月常远征还有{remain_days}天刷新！',
    ]
    await sv.broad_cast(msgs, 'ensei_reminder', 0.5)
