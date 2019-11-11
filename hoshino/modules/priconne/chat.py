'''
聊天吹水 for Princess Connect Re:Dive
'''


import re
import math
import random


from nonebot import on_command, CommandSession, MessageSegment
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import permission as perm

from hoshino.util import silence, delete_msg
from hoshino.res import R

__private_send_pic_cmd = '__send_pic_' + hex(random.randint(0x1000000000000000, 0xffffffffffffffff))[2:]

@on_command('沙雕机器人', aliases=('沙雕機器人',), only_to_me=False)
async def say_sorry(session: CommandSession):
    await session.send('ごめんなさい！嘤嘤嘤(〒︿〒)')

@on_command('arina-database', aliases=('jjc', 'JJC', 'JJC作业', 'JJC作业网', 'JJC数据库', 'jjc作业', 'jjc作业网', 'pjjc作业网', 'jjc数据库', 'pjjc数据库', 'JJC作業', 'JJC作業網', 'JJC數據庫', 'jjc作業', 'jjc作業網', 'jjc數據庫'))
async def say_arina_database(session: CommandSession):
    await session.send('公主连接Re:Dive 竞技场编成数据库\n日文：https://nomae.net/arenadb \n中文：https://pcrdfans.com/battle')


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


@on_natural_language(keywords={'咖啡'}, permission=perm.GROUP)
async def call_master(session:NLPSession):
    await session.send(MessageSegment.at(session.bot.config.SUPERUSERS[0]))


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



@on_command('ban_word', aliases=('rbq', 'RBQ', '憨批', '废物', '死妈', 'a片', 'A片', '崽种', '傻逼', '傻逼玩意', '没用东西', '傻B', '傻b', 'SB', 'sb', '煞笔', 'cnm', '爬', 'kkp'), only_to_me=True)
async def ban_word(session:CommandSession):
    await session.send('D区')
    await silence(session, 24*60*60)


@on_command('sayhello', aliases=('在', '在？', '在吗', '在么？', '在嘛', '在嘛？'))
async def sayhello(session:CommandSession):
    await session.send('はい！ほしのちゃんはいつもあなたのそばにいるよ')
