import pytz
import random
from datetime import datetime, timedelta
from collections import defaultdict

from nonebot import get_bot
from nonebot import CommandSession, MessageSegment
from nonebot import permission as perm
from hoshino.util import silence, concat_pic, pic2b64
from hoshino.service import Service, Privilege as Priv
from hoshino.res import R


__plugin_name__ = 'custom'
sv = Service('custom')

qks_url=["granbluefantasy.jp"]
qksimg=R.img('priconne/quick/qksimg.jpg').cqcode

xiaobao_aliases = ('迫害奉孝', '迫害孝宝')
xbimg=R.img('priconne/quick/xiaobao.png').cqcode


p1 = R.img('priconne/quick/qian.png').cqcode
p2 = R.img('priconne/quick/zhong.png').cqcode
p3 = R.img('priconne/quick/hou.png').cqcode


@sv.on_keyword(qks_url,normalize=True,event='group')
async def qks(bot,ctx):
    msg=f'爪巴\n{qksimg}'
    await bot.send(ctx,msg,at_sender=True)


@sv.on_command('xiaobao', aliases=xiaobao_aliases, only_to_me=False)
async def xiaobao(session:CommandSession):
    await session.send(f'您又迫害孝宝了！孝宝要哭了\n{xbimg}',at_sender=True)

@sv.on_rex(r'^([前中后])?rank', normalize=True, event='group')
async def rank_sheet(bot, ctx, match):
    is_qian = match.group(1) == '前'
    is_zhong= match.group(1) == '中'
    is_hou= match.group(1) == '后'
    if not is_qian and not is_hou and not is_zhong:
        await bot.send(ctx, '\n请问您要查前中后卫哪个的rank表？\n前rank\n后rank\n中rank', at_sender=True)
    else:
        await bot.send(ctx, '图片较大，请稍等片刻')
        if is_qian:
            await bot.send(ctx, f'前卫rank表：\n{p1}', at_sender=True)
        if is_zhong:
            await bot.send(ctx, f'中卫rank表：\n{p2}', at_sender=True)
        if is_hou:
            await bot.send(ctx, f'后卫rank表：\n{p3}', at_sender=True)
