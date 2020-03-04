import pytz
import random
from datetime import datetime

import nonebot

from hoshino import util
from hoshino.service import Service

sv = Service('hourcall', enable_on_default=False)
svtw = Service('pcr-arena-reminder-tw', enable_on_default=False)
svjp = Service('pcr-arena-reminder-jp', enable_on_default=False)

def get_config():
    return util.load_config(__file__)


def get_hour_call():
    """从HOUR_CALLS中挑出一组时报，每日更换，一日之内保持相同"""
    config = get_config()
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    hc_groups = config["HOUR_CALLS"]
    g = hc_groups[ now.day % len(hc_groups) ]
    return config[g]


@sv.scheduled_job('cron', hour='*')
async def hour_call():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    if 2 <= now.hour <= 4:
        return  # 宵禁 免打扰
    msg = get_hour_call()[now.hour]
    await sv.broad_cast(msg, 'hourcall', 0)


@svtw.scheduled_job('cron', hour='14', minute='45')
async def pcr_reminder_tw():
    msg = '骑士君、准备好背刺了吗？'
    await svtw.broad_cast(msg, 'pcr-reminder-tw', 0.2)


@svjp.scheduled_job('cron', hour='13', minute='45')
async def pcr_reminder_jp():
    msg = '骑士君、准备好背刺了吗？'
    await svjp.broad_cast(msg, 'pcr-reminder-jp', 0.2)
