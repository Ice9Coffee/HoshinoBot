import random
import hoshino
from hoshino import Service, aiorequests, priv

sv = Service('deepchat', manage_priv=priv.SUPERUSER, enable_on_default=False, visible=False)

@sv.on_message('group')
async def deepchat(bot, ctx):
    msg = ctx['message'].extract_plain_text()
    if not msg or random.random() > 0.025:
        return
    payload = {
        "msg": msg,
        "group": ctx['group_id'],
        "qq": ctx['user_id']
    }
    sv.logger.debug(payload)
    api = hoshino.config.deepchat.deepchat_api
    rsp = await aiorequests.post(api, data=payload, timeout=10)
    rsp = await rsp.json()
    sv.logger.debug(rsp)
    if rsp['msg']:
        await bot.send(ctx, rsp['msg'])
