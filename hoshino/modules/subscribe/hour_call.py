import os
import pytz
import ujson as json
import random
from datetime import datetime

import nonebot

from hoshino.log import logger
from hoshino.service import Service

sv = Service('hourcall', enable_on_default=False)
svtw = Service('pcr-arena-reminder-tw', enable_on_default=False)
svjp = Service('pcr-arena-reminder-jp', enable_on_default=False)

def get_config():
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_file, 'r') as f:
        config = json.load(f)
        return config


def get_hour_call():
    """从HOUR_CALLS中挑出一组时报，每日更换，一日之内保持相同"""
    config = get_config()
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    hc_groups = config["HOUR_CALLS"]
    g = hc_groups[ now.day % len(hc_groups) ]
    return config[g]


LAST_HOUR_CALL = -1

@sv.scheduled_job('cron', hour='*', minute='0-2', second='0', misfire_grace_time=30, coalesce=True)
async def hour_call(group_list):
    global LAST_HOUR_CALL
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    if LAST_HOUR_CALL == now.hour:
        return
    LAST_HOUR_CALL = now.hour

    if 2 <= now.hour <= 4:
        return  # 宵禁 免打扰

    msg = get_hour_call()[now.hour]
    for group, sid in group_list.items():
        try:
            await sv.bot.send_group_msg(self_id=random.choice(sid), group_id=group, message=msg)
            sv.logger.info(f'群{group} 投递hour_call成功')
        except nonebot.CQHttpError as e:
            sv.logger.error(f'群{group} 投递hour_call失败 {type(e)}')


@svtw.scheduled_job('cron', hour='6', minute='45', second='0', misfire_grace_time=120, coalesce=True) # = UTC+8 1445
async def pcr_reminder_tw(group_list):
    for group, sid in group_list.items():
        try:
            await svtw.bot.send_group_msg(self_id=random.choice(sid), group_id=group, message='骑士君、准备好背刺了吗？')
            svtw.logger.info(f'群{group} 投递pcr_reminder_tw成功')
        except nonebot.CQHttpError as e:
            svtw.logger.error(f'群{group} 投递pcr_reminder_tw失败 {type(e)}')


@svjp.scheduled_job('cron', hour='5', minute='45', second='0', misfire_grace_time=120, coalesce=True) # = UTC+8 1345
async def pcr_reminder_jp(group_list):
    for group, sid in group_list.items():
        try:
            await svjp.bot.send_group_msg(self_id=random.choice(sid), group_id=group, message='骑士君、准备好背刺了吗？')
            svjp.logger.info(f'群{group} 投递pcr_reminder_jp成功')
        except nonebot.CQHttpError as e:
            svjp.logger.error(f'群{group} 投递pcr_reminder_jp失败 {type(e)}')
