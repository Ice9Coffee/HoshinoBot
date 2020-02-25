import re
import math
import random


from nonebot import on_command, CommandSession, MessageSegment
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import permission as perm

from hoshino.log import logger
from hoshino.util import silence, delete_msg
from hoshino.res import R

__private_send_pic_cmd = '__send_pic_' + hex(random.randint(0x1000000000000000, 0xffffffffffffffff))[2:]

@on_command('沙雕机器人', aliases=('沙雕機器人',), only_to_me=False)
async def say_sorry(session: CommandSession):
    await session.send('ごめんなさい！嘤嘤嘤(〒︿〒)')


@on_command(__private_send_pic_cmd, only_to_me=False)
async def send_pic(session:CommandSession):
    pic = R.img(session.state['pic_name']).cqcode
    await session.send(pic)


@on_natural_language(keywords={'确实', '確實'}, only_to_me=False, only_short_message=True)
async def nlp_queshi(session:NLPSession):
    rex = re.compile(r'确实')
    if rex.search(session.msg_text):
        if random.random() < 0.05:
            return IntentCommand(90.0, __private_send_pic_cmd, args={'pic_name': '确实.jpg'})
        else:
            return None


@on_natural_language(keywords={'会战', '刀', '會戰'}, only_to_me=False, only_short_message=True)
async def nlp_clanba_time(session:NLPSession):
    if random.random() < 0.05:
        return IntentCommand(90.0, __private_send_pic_cmd, args={'pic_name': '我的天啊你看看都几点了.jpg'})
    else:
        return None


@on_natural_language(keywords={'内鬼', '內鬼'}, only_to_me=False, only_short_message=True)
async def nlp_neigui(session:NLPSession):
    if random.random() < 0.10:
        return IntentCommand(90.0, __private_send_pic_cmd, args={'pic_name': '内鬼.png'})
    else:
        return None


@on_command('老婆', aliases=('waifu', 'laopo'))
async def laopo(session:CommandSession):
    if not await perm.check_permission(session.bot, session.ctx, perm.SUPERUSER):
        session.state['pic_name'] = '喊谁老婆呢.jpg'
        await send_pic(session)
    else:
        await session.send('mua~')


@on_command('mua')
async def mua(session:CommandSession):
    await session.send('笨蛋~')


BANNED_WORD = ('rbq', 'RBQ', '憨批', '废物', '死妈', '崽种', '傻逼', '傻逼玩意', '没用东西', '傻B', '傻b', 'SB', 'sb', '煞笔', 'cnm', '爬', 'kkp', 'nmsl', 'D区', '口区')
@on_command('ban_word', aliases=BANNED_WORD, only_to_me=True)
async def ban_word(session:CommandSession):
    ctx = session.ctx
    msg_from = str(ctx['user_id'])
    if ctx['message_type'] == 'group':
        msg_from += f'@[群:{ctx["group_id"]}]'
    elif ctx['message_type'] == 'discuss':
        msg_from += f'@[讨论组:{ctx["discuss_id"]}]'
    logger.critical(f'Self: {ctx["self_id"]}, Message {ctx["message_id"]} from {msg_from}: {ctx["message"]}')
    await session.send(random.choice(BANNED_WORD), at_sender=True)
    await silence(session.ctx, 24*60*60)


@on_command('sayhello', aliases=('在', '在？', '在吗', '在么？', '在嘛', '在嘛？'))
async def sayhello(session:CommandSession):
    await session.send('はい！私はいつも貴方の側にいますよ！')
