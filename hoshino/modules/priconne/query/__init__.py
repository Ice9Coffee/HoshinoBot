import re
import math
import random

from nonebot import on_command, CommandSession, MessageSegment
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import permission as perm

from hoshino.util import silence, delete_msg
from hoshino.res import R


@on_natural_language(keywords={'rank', 'Rank', 'RANK'}, only_to_me=False, only_short_message=True)
async def nlp_rank(session:NLPSession):

    arg = session.msg_text.strip()
    is_jp = arg.find('日') >= 0
    is_tw = arg.find('台') >= 0 or arg.find('臺') >= 0

    p1 = R.img('priconne/quick/前卫rank.jpg').cqcode
    p2 = R.img('priconne/quick/中卫rank.jpg').cqcode
    p3 = R.img('priconne/quick/后卫rank.jpg').cqcode
    p4 = R.img('priconne/quick/台rank.png').cqcode

    if not is_jp and not is_tw:
        await session.send('请问您要查询日服还是台服的rank表？\n* 日rank\n* 台rank')
    else:
        await silence(session.ctx, 60)
        await session.send('rank表图片较大，请稍等片刻\n不定期搬运，来源见图片，广告与本bot无关，仅供参考')
        if is_jp:
            await session.send(f'日服rank表暂待更新')
        if is_tw:
            await session.send(f'R15-3 rank表：{p1}{p2}{p3}')


@on_natural_language(keywords={'pcr速查', 'PCR速查', 'pcr常用', 'PCR常用', 'pcr图书馆'}, only_to_me=False)
async def query_sites(session:NLPSession):
    msg='''繁中wiki：pcredivewiki.tw
日文wiki：gamewith.jp/pricone-re
日文wiki：appmedia.jp/priconne-redive
竞技场查询：pcrdfans.com/battle
竞技场查询：nomae.net/arenadb
NGA论坛：bbs.nga.cn/thread.php?fid=-10308342
日官网：priconne-redive.jp
台官网：www.princessconnect.so-net.tw'''
    await session.send(msg)
    await silence(session.ctx, 60)

@on_command('arina-database', aliases=('jjc', 'JJC', 'JJC作业', 'JJC作业网', 'JJC数据库', 'jjc作业', 'jjc作业网', 'pjjc作业网', 'jjc数据库', 'pjjc数据库', 'JJC作業', 'JJC作業網', 'JJC數據庫', 'jjc作業', 'jjc作業網', 'jjc數據庫'), only_to_me=False)
async def say_arina_database(session: CommandSession):
    await session.send('公主连接Re:Dive 竞技场编成数据库\n日文：https://nomae.net/arenadb \n中文：https://pcrdfans.com/battle')
