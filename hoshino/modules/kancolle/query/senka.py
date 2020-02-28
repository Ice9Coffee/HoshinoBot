from nonebot import MessageSegment as ms
from hoshino import aiorequests

from . import sv

_url = "http://203.104.209.7/kcscontents/information/image/rank{}.jpg"

@sv.on_rex(r'^人事表\s*(\d{6})', normalize=True, event='group')
async def rank_result(bot, ctx, match):
    rankid = match.group(1)
    yy, mm, server = int(rankid[0:2]), int(rankid[2:4]), int(rankid[4:6])
    if 13 <= yy and 1 <= mm <= 12 and 1 <= server <= 20:
        await bot.send(ctx, ms.image(_url.format(rankid)), at_sender=True)
