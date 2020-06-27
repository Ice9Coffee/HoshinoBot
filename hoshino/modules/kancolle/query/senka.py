import os
from nonebot import MessageSegment as ms
from hoshino import R

from . import sv

def rank_filename(yy, mm, ss):
    return f"rank{yy:02d}{mm:02d}{ss:02d}.jpg"

def rank_url(yy, mm, ss):
    return f"http://203.104.209.7/kcscontents/information/image/{rank_filename(yy, mm, ss)}"

def get_img_cq(yy, mm, ss):
    img = R.img('kancolle/senka/', rank_filename(yy, mm, ss))
    if os.path.exists(img.path):
        return img.cqcode
    else:
        return ms.image(rank_url(yy, mm, ss))


@sv.on_rex(r'^\*?人事表\s*(\d{6})')
async def rank_result(bot, ev):
    rankid = ev['match'].group(1)
    yy, mm, ss = int(rankid[0:2]), int(rankid[2:4]), int(rankid[4:6])
    if 13 <= yy and 1 <= mm <= 12 and 1 <= ss <= 20:
        await bot.send(ev, get_img_cq(yy, mm, ss))
