from nonebot import on_command, CommandSession, MessageSegment
from nonebot.permission import *
from .util import get_cqimg

'''
@on_command('setu', aliases=('涩图', '色图', '来点涩图', '来点色图', '来张涩图', '来张色图', '来点杏佬'), only_to_me=False)
async def setu(session: CommandSession):
    # xinglingling = MessageSegment.at(1418501385)
    # await session.send("[CQ:at, qq={0}] 出来发涩图啦！".format(1418501385))
    group_id = session.ctx['group_id']
    user_id = session.ctx['user_id']
    await session.bot.set_group_ban(group_id=group_id , user_id=user_id, duration=24*60)
'''

@on_command('seina', aliases=('来点星奏',), only_to_me=False)
async def seina(session: CommandSession):
    seg_setu = get_cqimg('星奏.png')
    await session.send(seg_setu)
    group_id = session.ctx['group_id']
    user_id = session.ctx['user_id']
    await session.bot.set_group_ban(group_id=group_id , user_id=user_id, duration=1*60)


@on_command('我有个朋友说他好了', aliases=('我朋友说他好了', ), only_to_me=False)
async def ddhaole(session: CommandSession):
    group_id = session.ctx['group_id']
    user_id = session.ctx['user_id']
    await session.bot.set_group_ban(group_id=group_id , user_id=user_id, duration=3*60)
    await session.send('那个朋友是不是你弟弟？')


@on_command('我好了', only_to_me=False)
async def nihaole(session: CommandSession):
    group_id = session.ctx['group_id']
    user_id = session.ctx['user_id']
    await session.bot.set_group_ban(group_id=group_id , user_id=user_id, duration=5*60)
    await session.send('不许好，憋回去！')

