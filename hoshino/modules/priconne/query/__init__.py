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

    p1 = R.img('priconne/quick/前卫rank.jpg').cqcode
    p2 = R.img('priconne/quick/中卫rank.jpg').cqcode
    p3 = R.img('priconne/quick/后卫rank.jpg').cqcode
    p4 = R.img('priconne/quick/台rank.png').cqcode

    await session.send(f'{p1}{p2}{p3}{p4}转载自 鏡華bot & 煌靈  仅供参考')
