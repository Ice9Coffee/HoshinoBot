import os
import pytz
import ujson as json
from datetime import datetime

import nonebot

from hoshino.log import logger


def get_config():
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_file, 'r') as f:
        config = json.load(f)
        return config


# UTC+8 1400 = UTC+9 1500 = UTC+0 0600 再提前半小时提醒
@nonebot.scheduler.scheduled_job('cron', hour='5', minute='30', second='0', misfire_grace_time=120, coalesce=True) 
async def enshu_reminder():
    logger.info('enshu_reminder start')

    msg = '[CQ:at,qq=all] 演习即将刷新！莫让下午的自己埋怨上午的自己：\n「演習」で練度向上！0/3\n[節分任務]節分演習！2DDor2DE演习S胜3次'
    bot = nonebot.get_bot()
    for group in get_config()["KANCOLLE_GROUP"]:
        try:
            await bot.send_group_msg(group_id=group, message=msg)
            logger.info(f'群{group} 投递enshu_reminder成功')
        except nonebot.CQHttpError as e:
            logger.error(f'群{group} 投递enshu_reminder失败 {type(e)}')

# UTC+8 2302 = UTC+0 1502
@nonebot.scheduler.scheduled_job('cron', hour='15', minute='2', second='0', misfire_grace_time=120, coalesce=True) 
async def setsubun_reminder():
    logger.info('setsubun_reminder start')

    msg = '[CQ:at,qq=all] 每日自省：[節分任務]節分演習！2DDor2DE演习S胜3次 完成了吗？'
    bot = nonebot.get_bot()
    for group in get_config()["KANCOLLE_GROUP"]:
        try:
            await bot.send_group_msg(group_id=group, message=msg)
            logger.info(f'群{group} 投递setsubun_reminder成功')
        except nonebot.CQHttpError as e:
            logger.error(f'群{group} 投递setsubun_reminder失败 {type(e)}')
