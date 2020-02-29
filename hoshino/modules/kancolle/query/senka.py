import os
from nonebot import MessageSegment as ms
from hoshino.res import R

from . import sv

def get_rank_id(yy, mm, ss):
    return f"rank{yy:02d}{mm:02d}{ss:02d}.jpg"

def get_url(yy, mm, ss):
    return f"http://203.104.209.7/kcscontents/information/image/{get_rank_id(yy, mm, ss)}"

def get_img_cq(yy, mm, ss):
    img = R.img('kancolle/senka/', get_rank_id(yy, mm, ss))
    if os.path.exists(img.path):
        return img.cqcode
    else:
        return ms.image(get_url(yy, mm, ss))


@sv.on_rex(r'^人事表\s*(\d{6})', normalize=True, event='group')
async def rank_result(bot, ctx, match):
    rankid = match.group(1)
    yy, mm, ss = int(rankid[0:2]), int(rankid[2:4]), int(rankid[4:6])
    if 13 <= yy and 1 <= mm <= 12 and 1 <= ss <= 20:
        await bot.send(ctx, get_img_cq(yy, mm, ss))
