from ..chara import Chara
from . import sv

_keywords = ('谁是', '是谁', '誰是', '是誰')

@sv.on_rex(r'^[谁誰]是(.{1,20})$', normalize=False)
async def whoisx(bot, ctx, match):
    await _whois(bot, ctx, match)

@sv.on_rex(r'^(.{1,20})是[谁誰]$', normalize=False)
async def xiswho(bot, ctx, match):
    await _whois(bot, ctx, match)


async def _whois(bot, ctx, match):
    name = match.group(1)
    chara = Chara.fromname(name)
    if chara.id == Chara.UNKNOWN:
        await bot.send(ctx, f'我也不知道"{name}"是谁...\n角色别称补全计划：github.com/Ice-Cirno/HoshinoBot/issues/5', at_sender=True)
        return
    
    msg = f'{chara.icon.cqcode} {chara.name}'
    await bot.send(ctx, msg, at_sender=True)
