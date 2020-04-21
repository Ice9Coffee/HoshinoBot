import pytz
from datetime import datetime
from hoshino import util
from hoshino.service import Service

sv = Service('hourcall', enable_on_default=False)

def get_hour_call():
    """从HOUR_CALLS中挑出一组时报，每日更换，一日之内保持相同"""
    config = util.load_config(__file__)
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
