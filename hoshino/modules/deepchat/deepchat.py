import random
import hoshino
from hoshino import Service, aiorequests, priv
from hoshino.util import DailyNumberLimiter
from hoshino.typing import CQEvent

sv = Service('deepchat', manage_priv=priv.SUPERUSER, enable_on_default=False, visible=False)
lmt = DailyNumberLimiter(10)

@sv.on_message('group')
async def deepchat(bot, ev: CQEvent):
    gid = ev.group_id

    if not lmt.check(gid):
        lmt.reset(gid)
    if lmt.get_num(gid):
        lmt.increase(gid)
        return

    msg = ev['message'].extract_plain_text()
    if not msg or random.random() > 0.060:
        return
    if not lmt.check(ev.group_id):
        return
    payload = {
        "msg": msg,
        "group": ev.group_id,
        "qq": ev.user_id,
    }
    sv.logger.debug(payload)
    api = hoshino.config.deepchat.deepchat_api
    rsp = await aiorequests.post(api, data=payload, timeout=10)
    rsp = await rsp.json()
    sv.logger.debug(rsp)
    if rsp['msg']:
        await bot.send(ev, rsp['msg'])
        lmt.increase(gid)
