import random

from hoshino import aiorequests
from nonebot import NoneBot
from hoshino.service import Service, Privilege

sv = Service('deepchat', manage_priv=Privilege.SUPERUSER, enable_on_default=False, visible=False)

api = 'http://127.0.0.1:7777/message'

@sv.on_message('group')
async def deepchat(bot:NoneBot, ctx):
    msg = ctx['message'].extract_plain_text()
    if random.random() > 0.030 or not msg:
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
