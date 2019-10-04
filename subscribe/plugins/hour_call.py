import os
import pytz
import json
from datetime import datetime

import nonebot


def get_config():
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_file, 'r') as f:
        config = json.load(f)
        return config


def get_auth_group():
    return get_config()["AUTH_GROUP"]


def get_hour_call():
    return get_config()["HOUR_CALL"]


@nonebot.scheduler.scheduled_job('cron', hour='*')
async def hour_call():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    msg = get_hour_call()[now.hour]

    bot = nonebot.get_bot()
    for group in get_auth_group():
        try:
            await bot.send_group_msg(group_id=group, message=msg)
            print(f'群{group} 投递成功')
        except nonebot.CQHttpError as e:
            print(e)
            print(f'Error：群{group} 投递失败')
