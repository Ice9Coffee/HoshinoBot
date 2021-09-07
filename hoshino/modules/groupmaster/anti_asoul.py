from datetime import timedelta
from hoshino import Service, priv, util
from hoshino.typing import CQEvent, CQHttpError, MessageSegment as ms

sv = Service('anti-asoul', enable_on_default=False)

@sv.on_keyword('嘉然', '然然', '嘉心糖', '嘉人')
@sv.on_rex(r'(嘉[\.\s]*(然|人))|(嘉[\.\s]*心[\.\s]*糖)')
async def anti_holo(bot, ev: CQEvent):
    priv.set_block_user(ev.user_id, timedelta(minutes=1))
    await util.silence(ev, 60, skip_su=False)
    await bot.send(ev, f'{ms.at(ev.user_id)} 你可少看点虚拟管人吧😅')
    try:
        await bot.delete_msg(self_id=ev.self_id, message_id=ev.message_id)
    except CQHttpError:
        pass
