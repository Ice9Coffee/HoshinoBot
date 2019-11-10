from nonebot import on_command, CommandSession, MessageSegment
from nonebot import permission as perm
from hoshino.res import R

__plugin_name__ = 'setu'

@on_command('seina', aliases=('来点星奏',), only_to_me=False)
async def seina(session: CommandSession):
    seg_setu = R.img('星奏.png').cqcode
    await session.send(seg_setu)
    # group_id = session.ctx['group_id']
    # user_id = session.ctx['user_id']
    # await session.bot.set_group_ban(group_id=group_id , user_id=user_id, duration=1*60)
    pass

@on_command('我有个朋友说他好了', aliases=('我朋友说他好了', ), only_to_me=False)
async def ddhaole(session: CommandSession):
    # group_id = session.ctx['group_id']
    # user_id = session.ctx['user_id']
    # await session.bot.set_group_ban(group_id=group_id , user_id=user_id, duration=3*60)
    # await session.send('那个朋友是不是你弟弟？')
    pass

@on_command('我好了', only_to_me=False)
async def nihaole(session: CommandSession):
    # group_id = session.ctx['group_id']
    # user_id = session.ctx['user_id']
    # await session.bot.set_group_ban(group_id=group_id , user_id=user_id, duration=5*60)
    # await session.send('不许好，憋回去！')
    pass
