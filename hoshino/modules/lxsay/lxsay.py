import re
import random
import os
import io
import base64
import hoshino
import textwrap
from hoshino.util import DailyNumberLimiter
from hoshino import R, Service, priv
from hoshino.util import pic2b64
from hoshino.typing import *
from PIL import Image, ImageFont, ImageDraw

FILE_PATH = os.path.dirname(__file__)

sv_help = '''鲁迅说的!
[鲁迅说xxx] 鲁迅说了啥
[你让鲁迅说点啥?]
'''.strip()

sv = Service(
    name='鲁迅说',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 是否可见
    enable_on_default=True,  # 是否默认启用
    bundle='娱乐',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_prefix(['鲁迅说'])
async def lx_say(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    if len(args) != 1:
        await bot.finish(ev, '你让鲁迅说点啥?', at_sender=True)
    content = args[0]
    if len(content) >= 25:
        await bot.finish(ev, '太长了, 鲁迅说不完!', at_sender=True)
    else:
        mes = get_lx_pic(content)
        await bot.finish(ev, mes)


def get_lx_pic(content):
    text = content
    para = textwrap.wrap(text, width=15)
    MAX_W, MAX_H = 480, 280
    bk_img = os.path.join(FILE_PATH, "luxun.jpg")
    print(FILE_PATH)
    FONTS_PATH = os.path.join(FILE_PATH, 'msyh.ttf')
    font = ImageFont.truetype(FONTS_PATH, 37)
    font2 = ImageFont.truetype(FONTS_PATH, 30)

    img_pil = Image.open(bk_img)
    # img_pil = Image.fromarray(bk_img)
    draw = ImageDraw.Draw(img_pil)

    current_h, pad = 300, 10
    for line in para:
        w, h = draw.textsize(line, font=font)
        draw.text(((MAX_W - w) / 2, current_h), line, font=font)
        current_h += h + pad

    draw.text((320, 400), "——鲁迅", font=font2, fill=(255, 255, 255))

    bio = io.BytesIO()
    img_pil.save(bio, format='PNG')
    base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
    mes = f"[CQ:image,file={base64_str}]"
    return mes
