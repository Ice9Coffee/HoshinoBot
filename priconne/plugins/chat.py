import re
import math
import random


from nonebot import on_command, CommandSession, MessageSegment
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.permission import *

from .util import get_cqimg, silence, delete_msg

@on_command('沙雕机器人', aliases=('沙雕',), only_to_me=False)
async def say_sorry(session: CommandSession):
    await session.send('ごめんなさい！嘤嘤嘤(〒︿〒)')

'''
@on_command('草', only_to_me=False)
async def say_kusa(session: CommandSession):
    await session.send('草')
    group_id = session.ctx['group_id']
    user_id = session.ctx['user_id']
    await session.bot.set_group_ban(group_id=group_id , user_id=user_id, duration=10*60)


@on_command('嘤嘤嘤', aliases=('嘤', '嘤嘤', '嘤嘤嘤嘤', '嘤嘤嘤嘤嘤', '嘤嘤嘤嘤嘤嘤',), only_to_me=False)
async def say_yingyingying(session: CommandSession):
    await session.send('嘤嘤怪确认！排除开始')
    group_id = session.ctx['group_id']
    user_id = session.ctx['user_id']
    await session.bot.set_group_ban(group_id=group_id , user_id=user_id, duration=45*60)


@on_command('给我笑')
async def say_ciya(session: CommandSession):
    ciya = MessageSegment.face(13)
    await session.send(ciya)
'''

__private_send_pic_cmd = '__send_pic_' + hex(random.randint(0x1000000000000000, 0xffffffffffffffff))[2:]

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
        return IntentCommand(90.0, __private_send_pic_cmd, args={'pic_name': '确实.jpg'})


@on_natural_language(keywords={'rank', 'Rank', 'RANK'}, only_to_me=False, only_short_message=True)
async def nlp_rank(session:NLPSession):
    arg = session.msg_text.strip()
    if re.search('前', arg):
        return IntentCommand(90.0, __private_send_pic_cmd, args={'pic_name': './priconne/quick/前卫rank.jpg'})
    if re.search('中', arg):
        return IntentCommand(90.0, __private_send_pic_cmd, args={'pic_name': './priconne/quick/中卫rank.jpg'})
    if re.search('后', arg):
        return IntentCommand(90.0, __private_send_pic_cmd, args={'pic_name': './priconne/quick/后卫rank.jpg'})



@on_natural_language(keywords={'套餐'}, only_to_me=False) 
async def sleep(session:NLPSession):
    arg = session.msg_text.strip()
    rex = re.compile(r'来(.*(份|个)(.*)(睡|茶)(.*))套餐')
    m = rex.search(arg)
    if m:
        length = len(m.group(1))
        sleep_time = 5*60*60 + round(math.sqrt(length) * 60 * 30 + 60 * random.randint(-15, 15))
        await silence(session, sleep_time, ignore_super_user=True)

