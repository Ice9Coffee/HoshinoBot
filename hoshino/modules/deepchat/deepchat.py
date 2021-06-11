import random
import hoshino
from hoshino import Service, aiorequests, priv

sv_help = '''
深度学习聊天
'''.strip()

sv = Service(
    name='深度学习',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 是否可见
    enable_on_default=True,  # 是否默认启用
    bundle='娱乐',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


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
