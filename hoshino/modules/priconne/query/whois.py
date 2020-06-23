from hoshino.typing import CQEvent, MessageSegment
from hoshino.util import FreqLimiter

from .. import chara
from . import sv

_lmt = FreqLimiter(5)

@sv.on_suffix(('是谁', '是誰'))
@sv.on_prefix(('谁是', '誰是'))
async def whois(bot, ev: CQEvent):
    uid = ev.user_id
    if not _lmt.check(uid):
        await bot.send(ev, '您查询得太快了，请稍等一会儿', at_sender=True)
        return
    _lmt.start_cd(uid)

    name = ev.message.extract_plain_text().strip()
    c = chara.fromname(name, star=0)
    if c.id == chara.UNKNOWN:
        # _lmt.start_cd(uid, 600)
        msg = MessageSegment.share(url='https://github.com/Ice-Cirno/HoshinoBot/issues/5', title='角色别称补全计划', content=f'兰德索尔似乎没有叫"{name}"的人')
        await bot.send(ev, msg)
        return

    msg = f'{c.icon.cqcode} {c.name}'
    await bot.send(ev, msg, at_sender=True)
