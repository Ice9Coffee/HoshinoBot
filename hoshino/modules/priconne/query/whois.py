from hoshino.util import FreqLimiter
from ..chara import Chara
from . import sv

from nonebot import MessageSegment
import random

_lmt = FreqLimiter(5)

RAINBOW_P = [
            f'{str(MessageSegment.at(438971718))}佬牛逼',
            f'{str(MessageSegment.at(438971718))}佬唯一滴神',
            f'我宣布{str(MessageSegment.at(438971718))}佬牛逼',
            ]

@sv.on_rex(r'^[谁誰]是\s*(.{1,20})$', normalize=False)
async def _whois(bot, ctx, match):

    uid = ctx['user_id']
    if not _lmt.check(uid):
        await bot.send(ctx, '您查询得太快了，请稍等一会儿', at_sender=True)
        return
    _lmt.start_cd(uid)

    message = ctx['raw_message'].strip('谁').strip('誰').strip('是')

    if message ==  'Ice-Cirno' or 'Ice咖啡' or '咖啡' or '咖啡佬':
        await bot.send(ctx, random.choice(RAINBOW_P))
        return

    name = match.group(1)
    chara = Chara.fromname(name)
    if chara.id == Chara.UNKNOWN:
        _lmt.start_cd(uid, 600)
        await bot.send(ctx, f'兰德索尔似乎没有叫"{name}"的人\n角色别称补全计划：github.com/Ice-Cirno/HoshinoBot/issues/5\n您的下次查询将于10分钟后可用', at_sender=True)
        return

    msg = f'{chara.icon.cqcode} {chara.name}'
    await bot.send(ctx, msg, at_sender=True)
