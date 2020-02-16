import os
import pytz
import random
import ujson as json
from datetime import datetime

import nonebot

from hoshino.service import Service


sv = Service('kc-reminder', enable_on_default=False)
utc_p8 = pytz.timezone('Asia/Shanghai')


@sv.scheduled_job('cron', hour='13', minute='30', misfire_grace_time=120, coalesce=True, timezone=utc_p8)
async def enshu_reminder(group_list):
    msg = '演习即将刷新！莫让下午的自己埋怨上午的自己：\n「演習」で練度向上！0/3'
    bot = sv.bot
    for group, sid in group_list.items():
        try:
            await bot.send_group_msg(self_id=random.choice(sid), group_id=group, message=msg)
            await bot.send_group_msg(self_id=random.choice(sid), group_id=group, message=f'[CQ:at,qq=all]')
            sv.logger.info(f'群{group} 投递enshu_reminder成功')
        except nonebot.CQHttpError as e:
            sv.logger.error(f'群{group} 投递enshu_reminder失败 {type(e)}')


# @sv.scheduled_job('cron', hour='23', minute='2', misfire_grace_time=120, coalesce=True, timezone=utc_p8)
async def setsubun_reminder(group_list):
    msg = '每日自省：[節分任務]節分演習！2DDor2DE演习S胜3次 完成了吗？'
    bot = sv.bot
    for group, sid in group_list.items():
        try:
            await bot.send_group_msg(self_id=random.choice(sid), group_id=group, message=msg)
            await bot.send_group_msg(self_id=random.choice(sid), group_id=group, message=f'[CQ:at,qq=all]')
            sv.logger.info(f'群{group} 投递setsubun_reminder成功')
        except nonebot.CQHttpError as e:
            sv.logger.error(f'群{group} 投递setsubun_reminder失败 {type(e)}')


@sv.scheduled_job('cron', day='12-14', hour='22', misfire_grace_time=120, coalesce=True, timezone=utc_p8)
async def ensei_reminder(group_list):
    now = datetime.now(utc_p8)
    remain_days = 15 - now.day
    msg = f'【远征提醒小助手】月常远征还有{remain_days}天刷新！'
    bot = sv.bot
    for group, sid in group_list.items():
        try:
            await bot.send_group_msg(self_id=random.choice(sid), group_id=group, message=msg)
            await bot.send_group_msg(self_id=random.choice(sid), group_id=group, message=f'[CQ:at,qq=all]')
            sv.logger.info(f'群{group} 投递ensei_reminder成功')
        except nonebot.CQHttpError as e:
            sv.logger.error(f'群{group} 投递ensei_reminder失败 {type(e)}')
