from datetime import timedelta
from hoshino import Service, priv, util
from hoshino.typing import CQEvent, CQHttpError, MessageSegment as ms

sv = Service('loli-is-justice', enable_on_default=False, visible=False)

@sv.on_keyword('炼铜', '恋童')
async def _(bot, ev: CQEvent):
    priv.set_block_user(ev.user_id, timedelta(hours=1))
    await util.silence(ev, 3600, skip_su=False)
    await bot.send(ev, f'{ms.at(ev.user_id)} 控二次元萝莉管你毛事？肿瘤痴差不多得了😅')
    try:
        await bot.delete_msg(self_id=ev.self_id, message_id=ev.message_id)
    except CQHttpError:
        pass
