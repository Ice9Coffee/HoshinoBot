import aiohttp
import requests
import hoshino
import os
from hoshino import R, Service, priv

sv_help = '''
不要沉迷二次元, 偶尔也要三次元一下啊
输入cos | coser 随机获取一张cos图
'''.strip()

sv = Service(
    name='Cos图',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 是否可见
    enable_on_default=True,  # 是否默认启用
    bundle='娱乐',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助-Cos图"])
async def helper(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


@sv.on_fullmatch(('coser', 'cos'))
async def cosPic(bot, ctx):
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
    msg = f'[CQ:image,file={imgUrl}]'.format(imgUrl=imgUrl)
    await bot.send(ctx, msg)
