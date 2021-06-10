# Repository: https://github.com/Lancercmd/Reloader
# Lancercmd / Reloader 使用 GPLv3 协议
# nonebot: https://github.com/richardchien/nonebot
# richardchien / nonebot 使用 MIT 协议
# 确保 nonebot >= 1.5.0
# 确保 bot.run(use_reloader=True)
from nonebot import CommandSession, on_command
from os import path

import nonebot
from .loop import Counter  # 借助 use_reloader 实现当模块发生变化时自动重载整个 Python

init = path.join(path.dirname(__file__), 'loop') + '.py'
if not path.exists(init):
    content = '''class Counter:
    count = 0'''
    with open(init, 'w') as file:
        file.write(content)

bot = nonebot.get_bot()
SUPERUSERS = bot.config.SUPERUSERS  # 获取 SUPERUSERS


@on_command('reload', aliases=('reboot', '重启', '重载'), only_to_me=True)
async def reload(session: CommandSession):
    uid = session.event.user_id
    if not uid in SUPERUSERS:  # SUPERUSERS: list
        return
    count = Counter.count + 1
    content = f'''class Counter:
    count = {count}'''
    with open(init, 'w') as file:
        file.write(content)
    await session.finish('重启中~')
