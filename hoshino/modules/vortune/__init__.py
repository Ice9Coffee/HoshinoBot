# -*- coding: utf-8 -*-

from . import main
from . import utils
from hoshino import R, Service, priv

sv_help = '''
- [抽签] 抽签|今日人品|今日运势|人品|运势
'''.strip()

sv = Service(
    name='抽签',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 是否可见
    enable_on_default=True,  # 是否默认启用
    bundle='查询',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_rex('抽签|今日人品|今日运势|人品|运势')
async def entranceFunction(bot, ev):
    msg = str(ev["raw_message"])
    userGroup = ev["group_id"]
    userQQ = ev["user_id"]
    await utils.initialization()
    await main.handlingMessages(msg, bot, userGroup, userQQ, ev)
