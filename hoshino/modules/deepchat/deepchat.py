import random

from hoshino import aiorequests
from nonebot import NoneBot
from hoshino import util
from hoshino.service import Service, Privilege

sv = Service('deepchat', manage_priv=Privilege.SUPERUSER, enable_on_default=False, visible=False)

api = util.load_config(__file__)['deepchat_api']

@sv.on_message('group')
async def deepchat(bot:NoneBot, ctx):
    msg = ctx['message'].extract_plain_text()
    if not msg or random.random() > 0.025:
        return
    payload = {
        "msg": msg,
        "group": ctx['group_id'],
        "qq": ctx['user_id']
    }
    sv.logger.info(payload)
    rsp = await aiorequests.post(api, data=payload)
    j = await rsp.json()
    sv.logger.info(j)
    if j['msg']:
        await bot.send(ctx, j['msg'])
