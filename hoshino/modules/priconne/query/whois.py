from hoshino.typing import CQEvent
from hoshino.util import FreqLimiter

from ..chara import Chara
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

    name = ev.message.extract_plain_text()
    chara = Chara.fromname(name, star=0)
    if chara.id == Chara.UNKNOWN:
        _lmt.start_cd(uid, 600)
        await bot.send(ev, f'兰德索尔似乎没有叫"{name}"的人\n角色别称补全计划：github.com/Ice-Cirno/HoshinoBot/issues/5\n您的下次查询将于10分钟后可用', at_sender=True)
        return

    msg = f'{chara.icon.cqcode} {chara.name}'
    await bot.send(ev, msg, at_sender=True)
