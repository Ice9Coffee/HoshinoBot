import re
import math
import random

from nonebot import on_command, CommandSession, MessageSegment
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import permission as perm

from hoshino.util import silence, delete_msg
from hoshino.res import R
from hoshino.service import Service

sv = Service('pcr-query')

p1 = R.img('priconne/quick/r15-3.png').cqcode
p4 = R.img('priconne/quick/r16-4-1.png').cqcode
p5 = R.img('priconne/quick/r16-4-2.png').cqcode
p6 = R.img('priconne/quick/r16-4-3.png').cqcode


@sv.on_rex(r'^(\*?([日台])服?)?rank', normalize=True, event='group')
async def rank_sheet(bot, ctx, match):
    is_jp = match.group(2) == '日'
    is_tw = match.group(2) == '台'
    if not is_jp and not is_tw:
        await bot.send(ctx, '\n请问您要查询日服还是台服的rank表？\n*日rank表\n*台rank表', at_sender=True)
    else:
        await silence(ctx, 60)
        await bot.send(ctx, 'rank推荐表图片较大，请稍等片刻\n※不定期搬运，来源见图片\n※广告与本bot无关，仅供参考')
        if is_jp:
            await bot.send(ctx, f'R16-4 rank表：{p4}{p5}{p6}', at_sender=True)
        if is_tw:
            await bot.send(ctx, f'R15-3 rank表：{p1}', at_sender=True)


@sv.on_rex(r'^(pcr(速查|常用)|图书馆)', normalize=True, event='group')
async def query_sites(bot, ctx, match):
    msg='''
图书馆(繁中)：pcredivewiki.tw
日文wiki：gamewith.jp/pricone-re
日文wiki：appmedia.jp/priconne-redive
竞技场(台日)：pcrdfans.com/battle
竞技场(日)：nomae.net/arenadb
NGA论坛：bbs.nga.cn/thread.php?fid=-10308342
日官网：priconne-redive.jp
台官网：www.princessconnect.so-net.tw'''
    await bot.send(ctx, msg, at_sender=True)
    await silence(ctx, 60)


@sv.on_command('arina-database', aliases=('jjc', 'JJC', 'JJC作业', 'JJC作业网', 'JJC数据库', 'jjc作业', 'jjc作业网', 'pjjc作业网', 'jjc数据库', 'pjjc数据库', 'JJC作業', 'JJC作業網', 'JJC數據庫', 'jjc作業', 'jjc作業網', 'jjc數據庫'), only_to_me=False)
async def say_arina_database(session: CommandSession):
    await session.send('公主连接Re:Dive 竞技场编成数据库\n日文：https://nomae.net/arenadb \n中文：https://pcrdfans.com/battle')


@sv.on_keyword({'黄骑充电', '酒鬼充电'}, normalize=True, event='group')
async def yukari_sheet(bot, ctx):
    msg = f'''{R.img('priconne/quick/黄骑充电.jpg').cqcode}
※黄骑四号位例外较多
※图为PVP测试
※对面羊驼或中后卫坦时 有可能充歪
※我方羊驼算一号位'''
    await bot.send(ctx, msg, at_sender=True)


@sv.on_rex(r'^(一个顶俩|(成语)?接龙)', normalize=True, event='group')
async def dragon(bot, ctx, match):
    msg = f"\n拼音对照表：{R.img('priconne/KyaruMiniGame/注音文字.jpg').cqcode}\n龍的探索者們 小遊戲單字表 https://hanshino.nctu.me/online/KyaruMiniGame\n镜像 hoshino.monster/KyaruMiniGame\n网站内有全词条和搜索，可能需要科学上网"
    await bot.send(ctx, msg, at_sender=True)
