import os
import re
from io import BytesIO

from PIL import Image

from hoshino import R, aiorequests
from hoshino.typing import CQEvent
from hoshino.typing import MessageSegment as ms

from . import sv

senka_dir = R.img('kancolle/senka/').path
os.makedirs(senka_dir, exist_ok=True)

def rank_filename(yy, mm, ss):
    return f"rank{yy:02d}{mm:02d}{ss:02d}.jpg"

def rank_url(yy, mm, ss):
    return f"http://203.104.209.7/kcscontents/information/image/{rank_filename(yy, mm, ss)}"

async def get_img(yy, mm, ss):
    img = R.img('kancolle/senka/', rank_filename(yy, mm, ss))
    if not os.path.exists(img.path):
        link = rank_url(yy, mm, ss)
        resp = await aiorequests.get(link, stream=True)
        if 200 == resp.status_code:
            if re.search(r'image', resp.headers['content-type'], re.I):
                i = Image.open(BytesIO(await resp.content))
                i.save(img.path)
    return img if img.exist else None

syntax_rex = re.compile(r'^\d{6}$')

@sv.on_prefix('人事表')
async def rank_result(bot, ev: CQEvent):
    m = syntax_rex.match(ev.message.extract_plain_text().strip())
    if not m:
        await bot.finish(ev, "用法：人事表yymmss\n例：查询20年07月吴镇(02号服务器)\n> 人事表200702")
    rankid = m.group()
    yy, mm, ss = int(rankid[0:2]), int(rankid[2:4]), int(rankid[4:6])
    if 13 <= yy and 1 <= mm <= 12 and 1 <= ss <= 20:
        img = await get_img(yy, mm, ss)
        if img:
            await bot.send(ev, img.cqcode)
        else:
            await bot.send(ev, "人事表获取失败")
