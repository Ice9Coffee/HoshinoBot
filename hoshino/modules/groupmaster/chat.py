import random

from nonebot import on_command

from hoshino import R, Service, priv, util


# basic function for debug, not included in Service('chat')
@on_command('zai?', aliases=('在?', '在？', '在吗', '在么？', '在嘛', '在嘛？'), only_to_me=True)
async def say_hello(session):
    await session.send('はい！私はいつも貴方の側にいますよ！')


sv = Service('chat', visible=False)

@sv.on_fullmatch('沙雕机器人')
async def say_sorry(bot, ev):
    await bot.send(ev, 'ごめんなさい！嘤嘤嘤(〒︿〒)')


@sv.on_fullmatch(('老婆', 'waifu', 'laopo'), only_to_me=True)
async def chat_waifu(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, R.img('laopo.jpg').cqcode)
    else:
        await bot.send(ev, 'mua~')


@sv.on_fullmatch('老公', only_to_me=True)
async def chat_laogong(bot, ev):
    await bot.send(ev, '你给我滚！', at_sender=True)


@sv.on_fullmatch('mua', only_to_me=True)
async def chat_mua(bot, ev):
    await bot.send(ev, '笨蛋~', at_sender=True)


@sv.on_fullmatch('来点星奏')
async def seina(bot, ev):
    await bot.send(ev, R.img('星奏.png').cqcode)


@sv.on_fullmatch('auto轴')
async def auto(bot, ev):
    await bot.send(ev, auto)
auto = f'''[CQ:xml,data=<?xml version="1.0" encoding="utf-8" ?><msg templateID="123" action="web" brief="腾讯文档 的分享" serviceID="1" url="https://docs.qq.com/sheet/DSlhtb0NQZUVQU2xt?tab=BB08J2"><item layout="2"><picture cover="http://pub.idqqimg.com/pc/misc/files/20190529/32e36b5d6f1b71fd3ddd129346c8f9c9.png" /><title>Auto作业...</title><summary>腾讯文档</summary></item><source url="" icon="https://pub.idqqimg.com/pc/misc/files/20180522/e84554865e704ee4a1da332568335bec.png" name="腾讯文档" appid="101458937" action="app" actionData="" a_actionData="com.tencent.docs" i_actionData="docs" /></msg>,resid=60]'''


# ============================================ #



nyb_player = f'''{R.img('newyearburst.gif').cqcode}
正在播放：New Year Burst
──●━━━━ 1:05/1:30
⇆ ㅤ◁ ㅤㅤ❚❚ ㅤㅤ▷ ㅤ↻
'''.strip()

@sv.on_keyword(('春黑', '新黑'))
async def new_year_burst(bot, ev):
    if random.random() < 0.02:
        await bot.send(ev, nyb_player)
