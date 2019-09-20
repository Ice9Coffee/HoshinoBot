from nonebot import on_command, CommandSession, MessageSegment
from nonebot.permission import *

@on_command('沙雕机器人', aliases=('沙雕',), only_to_me=False)
async def say_sorry(session: CommandSession):
    await session.send('ごめんなさい！嘤嘤嘤(〒︿〒)')


# @on_command('草', only_to_me=False)
# async def say_kusa(session: CommandSession):
#     await session.send('草')
#     group_id = session.ctx['group_id']
#     user_id = session.ctx['user_id']
#     await session.bot.set_group_ban(group_id=group_id , user_id=user_id, duration=10*60)


@on_command('嘤嘤嘤', aliases=('嘤', '嘤嘤', '嘤嘤嘤嘤', '嘤嘤嘤嘤嘤', '嘤嘤嘤嘤嘤嘤',), only_to_me=False)
async def say_yingyingying(session: CommandSession):
    await session.send('嘤嘤怪确认！排除开始')
    group_id = session.ctx['group_id']
    user_id = session.ctx['user_id']
    await session.bot.set_group_ban(group_id=group_id , user_id=user_id, duration=10*60)


@on_command('给我笑')
async def say_ciya(session: CommandSession):
    ciya = MessageSegment.face(13)
    await session.send(ciya)


@on_command('arina-database', aliases=('jjc', 'jjc作业', 'jjc作业网', 'pjjc作业网', 'jjc数据库', 'pjjc数据库'))
async def say_arina_database(session: CommandSession):
    await session.send('公主连接Re:Dive 竞技场编成数据库\n日文：https://nomae.net/arenadb \n中文：https://pcrdfans.com/battle')


