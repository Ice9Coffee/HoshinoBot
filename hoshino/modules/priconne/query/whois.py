from hoshino.util import FreqLimiter
from ..chara import Chara
from . import sv

lmt = FreqLimiter(30)

@sv.on_rex(r'^[谁誰]是(.{1,20})$', normalize=False)
async def _whois(bot, ctx, match):
    uid = ctx['user_id']
    if not lmt.check(uid) and uid not in sv.bot.config.SUPERUSERS:
        await bot.send(ctx, '您查询得太快了，请稍等半分钟', at_sender=True)
        return
    lmt.start_cd(uid)

    name = match.group(1)
    chara = Chara.fromname(name)
    if chara.id == Chara.UNKNOWN:
        await bot.send(ctx, f'我也不知道"{name}"是谁\n角色别称补全计划：github.com/Ice-Cirno/HoshinoBot/issues/5', at_sender=True)
        return

    msg = f'{chara.icon.cqcode} {chara.name}'
    await bot.send(ctx, msg, at_sender=True)
