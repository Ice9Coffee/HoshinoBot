import re
import math
import random

from nonebot import on_command, CommandSession, MessageSegment
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import permission as perm

from hoshino.util import silence, delete_msg
from hoshino.res import R


@on_natural_language(keywords={'rank', 'Rank', 'RANK'}, only_to_me=True, only_short_message=True)
async def nlp_rank(session:NLPSession):

    p1 = R.img('priconne/quick/前卫rank.jpg').cqcode
    p2 = R.img('priconne/quick/中卫rank.jpg').cqcode
    p3 = R.img('priconne/quick/后卫rank.jpg').cqcode
    p4 = R.img('priconne/quick/台rank.png').cqcode

    await session.send('rank表图片较大，请稍等片刻\n不定期搬运，来源见图片，广告与本bot无关，仅供参考')
    await session.send(p1 + p2 + p3)
    await session.send(p4)
    await silence(session, 60)


@on_natural_language(keywords={'pcr速查', 'PCR速查', 'pcr常用', 'PCR常用', '图书馆'}, only_to_me=True)
async def query_sites(session:NLPSession):
    msg='''繁中wiki：pcredivewiki.tw
日文wiki：gamewith.jp/pricone-re
日文wiki：appmedia.jp/priconne-redive
竞技场查询：www.pcrdfans.com/battle
NGA论坛：bbs.nga.cn/thread.php?fid=-10308342
日官网：priconne-redive.jp
台官网：www.princessconnect.so-net.tw'''
    await session.send(msg)
    await silence(session, 60)
