import aiohttp
import requests
import hoshino
import os
import hashlib
from .Coser import Coser, saveToDb
from hoshino import R, Service, priv
from hoshino.typing import CQEvent
from hoshino.util import FreqLimiter, DailyNumberLimiter

sv_help = '''
不要沉迷二次元, 偶尔也要三次元一下啊
输入cos | coser 随机获取一张cos图
'''.strip()

sv = Service(
    name='cos图',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 是否可见
    enable_on_default=True,  # 是否默认启用
    bundle='娱乐',  # 属于哪一类
    help_=sv_help  # 帮助文本
)

_max = 5
EXCEED_NOTICE = f'今天已经要了{_max}张图了~~~明天进货吧~~~!'
_limit = DailyNumberLimiter(_max)


@sv.on_fullmatch(["帮助-Cos图"])
async def helper(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


@sv.on_fullmatch(('coser', 'cos'))
async def cosPic(bot, ctx: CQEvent):
    if not _limit.check(ctx.user_id):
        await bot.send(ctx, EXCEED_NOTICE, at_sender=True)

    async with aiohttp.TCPConnector(verify_ssl=False) as connector:
        async with aiohttp.request(
                method='GET',
                url='http://api.repeater.vip/cos-img/',
                connector=connector,
        ) as resp:
            imgUrl = await resp.text()
    if len(imgUrl) == 0:
        await bot.send(ctx, '没有结果')
        return
    # 记录图片
    md5 = hashlib.md5()
    b = imgUrl.encode(encoding='utf-8')
    md5.update(b)
    str_md5 = md5.hexdigest()
    saveToDb(0, 'api.repeater.vip', 0, '', imgUrl, 'cos', str_md5, '')
    msg = f'[CQ:image,file={imgUrl}]'.format(imgUrl=imgUrl)
    await bot.send(ctx, msg, at_sender=True)
