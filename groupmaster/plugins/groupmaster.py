from nonebot import on_command, CommandSession
from nonebot.permission import *
import re

#, permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER)

re_silence = re.compile(r'来.?份(.*)睡眠套餐')

@on_command('silence', aliases=('睡眠套餐', '休眠套餐', '精致睡眠', '来一份精致睡眠套餐', re_silence), only_to_me=False) 
async def silence(session: CommandSession):
    group_id = session.ctx['group_id']
    user_id = session.ctx['user_id']
    await session.bot.set_group_ban(group_id=group_id , user_id=user_id, duration=8*60*60)


@silence.args_parser
async def _(session: CommandSession):
    pass
