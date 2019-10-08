'''
聊天吹水 for Princess Connect Re:Dive
'''


import re
import math
import random


from nonebot import on_command, CommandSession, MessageSegment
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.permission import *

from .util import get_cqimg, silence, delete_msg

__private_send_pic_cmd = '__send_pic_' + hex(random.randint(0x1000000000000000, 0xffffffffffffffff))[2:]

@on_command('沙雕机器人', aliases=('沙雕',), only_to_me=False)
async def say_sorry(session: CommandSession):
    await session.send('ごめんなさい！嘤嘤嘤(〒︿〒)')

@on_command('arina-database', aliases=('jjc', 'JJC', 'JJC作业', 'JJC作业网', 'JJC数据库', 'jjc作业', 'jjc作业网', 'pjjc作业网', 'jjc数据库', 'pjjc数据库'))
async def say_arina_database(session: CommandSession):
    await session.send('公主连接Re:Dive 竞技场编成数据库\n日文：https://nomae.net/arenadb \n中文：https://pcrdfans.com/battle')


@on_command(__private_send_pic_cmd, only_to_me=False)
async def send_pic(session:CommandSession):
    pic = get_cqimg(session.state['pic_name'])
    await session.send(pic)


@on_natural_language(keywords={'确实'}, only_to_me=False, only_short_message=True)
async def nlp_queshi(session:NLPSession):
    rex = re.compile(r'确实')
    if rex.search(session.msg_text):
        if random.random() < 0.618:
            return IntentCommand(90.0, __private_send_pic_cmd, args={'pic_name': '确实.jpg'})
        else:
            return None


@on_natural_language(keywords={'会战', '刀'}, only_to_me=False, only_short_message=True)
async def nlp_clanba_time(session:NLPSession):
    if random.random() < 0.10:
        return IntentCommand(90.0, __private_send_pic_cmd, args={'pic_name': '我的天啊你看看都几点了.jpg'})
    else:
        return None


@on_natural_language(keywords={'内鬼'}, only_to_me=False, only_short_message=True)
async def nlp_neigui(session:NLPSession):
    if random.random() < 0.30:
        return IntentCommand(90.0, __private_send_pic_cmd, args={'pic_name': '内鬼.jpg'})
    else:
        return None



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



@on_natural_language(keywords={'套餐'}, only_to_me=False)
async def sleep(session:NLPSession):
    arg = session.msg_text.strip()
    rex = re.compile(r'来(.*(份|个)(.*)(睡|茶)(.*))套餐')
    base = 0 if '午' in arg else 5*60*60
    m = rex.search(arg)
    if m:
        length = len(m.group(1))
        sleep_time = base + round(math.sqrt(length) * 60 * 30 + 60 * random.randint(-15, 15))
        await silence(session, sleep_time, ignore_super_user=True)


@on_natural_language(keywords={'咖啡'})
async def call_master(session:NLPSession):
    session.send(MessageSegment.at(session.bot.config.SUPERUSERS[0]))


@on_command('老婆', aliases=('waifu', 'laopo'))
async def laopo(session:CommandSession):
    if not await check_permission(session.bot, session.ctx, SUPERUSER):
        session.state['pic_name'] = '喊谁老婆呢.jpg'
        await send_pic(session)
    else:
        await session.send('mua~')


@on_command('mua')
async def mua(session:CommandSession):
    await session.send('笨蛋~')



@on_command('ban_word', aliases=('rbq', 'RBQ', '憨批', '废物', '死妈', 'a片', 'A片', '崽种', '傻逼', '傻逼玩意', '没用东西', '傻B', '傻b', 'SB', 'sb', '煞笔', 'cnm', '爬'), only_to_me=True)
async def ban_word(session:CommandSession):
    await session.send('D区')
    await silence(session, 24*60*60)


@on_command('sayhello', aliases=('在', '在？', '在吗', '在么？', '在嘛', '在嘛？'))
async def sayhello(session:CommandSession):
    await session.send('はい！ほしのちゃんはいつもあなたのそばにいるよ')


@on_command('help', aliases=('帮助', '说明', '使用说明'), only_to_me=False)
async def send_help(session:CommandSession):
    msg='''
目前支持的功能：[]替换为实际参数 注意使用空格分隔
- 会战管理：详见github.com/Ice-Cirno/HoshinoBot
- jjc查询：怎么拆 [角色1] [角色2] [...]
- 翻译：翻译 [文本]
- 查看rank推荐表：[前|中|后]卫rank表
- 查看卡池：卡池资讯

以下功能需at机器人：请手动at，复制无效
- 阅览官方四格：官漫[章节数] @bot
- 十连转蛋：来发十连 @bot
- 单抽转蛋：来发单抽 @bot
- 查看新番：来点新番 @bot
- 查阅jjc数据库网址：jjc作业网 @bot

主动推送：（如需开启/关闭请联系维护组）
- 时报
- 背刺时间提醒
- プリコネRe:Dive官方四格推送
- 番剧更新推送

以及其他隐藏功能:)
'''.strip()
    await session.send(msg)
