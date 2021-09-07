import os
import re
from io import BytesIO

from PIL import Image

from hoshino import R, aiorequests
from hoshino.typing import CQEvent

from . import sv

senka_dir = R.img('kancolle/senka/').path
os.makedirs(senka_dir, exist_ok=True)

SERVERS = '''
[01] 横镇 [02] 吴镇
[03] 佐镇 [04] 舞鹤
[05] 大凑 [06] 特鲁克
[07] 林加 [08] 拉包尔
[09] 肖特兰 [10] 布因
[11] 塔威塔威 [12] 帕劳
[13] 文莱 [14] 单冠湾
[15] 幌筵 [16] 宿毛湾
[17] 鹿屋 [18] 岩川
[19] 佐伯湾 [20] 柱岛
'''.strip()

def rank_filename(yy, mm, ss):
    return f"rank{yy:02d}{mm:02d}{ss:02d}.jpg"

def rank_url(yy, mm, ss):
    return f"http://203.104.209.7/kcscontents/information/image/{rank_filename(yy, mm, ss)}"

async def get_img(yy, mm, ss):
    img = R.img('kancolle/senka/', rank_filename(yy, mm, ss))
    if not img.exist:
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
        await bot.finish(ev, "用法：人事表yymmss\n例：查询21年06月吴镇\n> 人事表210602\n※服务器编号见https://senka.su/")
    rankid = m.group()
    yy, mm, ss = int(rankid[0:2]), int(rankid[2:4]), int(rankid[4:6])
    if yy >= 13 and 1 <= mm <= 12 and 1 <= ss <= 20:
        img = await get_img(yy, mm, ss)
        if img:
            await bot.send(ev, img.cqcode)
        else:
            await bot.send(ev, f"人事表获取失败！\n这可能是由于20{yy:02d}年{mm}月战果尚未发放或网络异常")
    else:
        await bot.finish(ev, f"参数异常：欲查询20{yy:02d}年{mm}月服务器{ss}不合法\n服务器一览：\n{SERVERS}")
