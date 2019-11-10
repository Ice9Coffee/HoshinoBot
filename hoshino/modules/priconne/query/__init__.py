import re
import math
import random

from nonebot import on_command, CommandSession, MessageSegment
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import permission as perm


from hoshino.util import silence, delete_msg
from hoshino.res import R

__private_send_pic_cmd = '__send_pic_' + hex(random.randint(0x1000000000000000, 0xffffffffffffffff))[2:]
@on_command(__private_send_pic_cmd, only_to_me=False)
async def send_pic(session:CommandSession):
    pic = R.img(session.state['pic_name']).cqcode
    await session.send(pic)


@on_natural_language(keywords={'rank', 'Rank', 'RANK'}, only_to_me=False, only_short_message=True)
async def nlp_rank(session:NLPSession):
    arg = session.msg_text.strip()
    if re.search('前', arg):
        return IntentCommand(90.0, __private_send_pic_cmd, args={'pic_name': './priconne/quick/前卫rank.jpg'})
    if re.search('中', arg):
        return IntentCommand(90.0, __private_send_pic_cmd, args={'pic_name': './priconne/quick/中卫rank.jpg'})
    if re.search('后', arg):
        return IntentCommand(90.0, __private_send_pic_cmd, args={'pic_name': './priconne/quick/后卫rank.jpg'})
    if re.search('rank推荐表', arg, re.I):
        session.send('输入前/中/后卫rank表以查看')
