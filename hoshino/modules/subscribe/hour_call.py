import os
import pytz
import ujson as json
from datetime import datetime

import nonebot

from hoshino.log import logger
from hoshino.service import Service

sv = Service('hourcall', enable_on_default=False)

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
    for group in group_list:
        try:
            await sv.bot.send_group_msg(group_id=group, message=msg)
            sv.logger.info(f'群{group} 投递hour_call成功')
        except nonebot.CQHttpError as e:
            sv.logger.error(f'群{group} 投递hour_call失败 {type(e)}')


@nonebot.scheduler.scheduled_job('cron', hour='5-6', minute='45', second='0', misfire_grace_time=120, coalesce=True) # = UTC+8 1445
async def pcr_reminder():
    logger.info('pcr_reminder start')

    is_jp = (5 == datetime.now(pytz.timezone('UTC')).hour)

    msg = f'一{"三" if is_jp else "四"}四五。骑士君、准备好背刺了吗？'
    bot = nonebot.get_bot()
    for group in get_config()["PCR_GROUP_JP" if is_jp else "PCR_GROUP_TW"]:
        try:
            await bot.send_group_msg(group_id=group, message=msg)
            logger.info(f'群{group} 投递pcr_reminder成功')
        except nonebot.CQHttpError as e:
            logger.error(f'群{group} 投递pcr_reminder失败 {type(e)}')
