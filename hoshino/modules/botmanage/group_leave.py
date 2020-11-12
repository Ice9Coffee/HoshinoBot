import re
from hoshino import sucmd
from hoshino.typing import CommandSession

@sucmd('quit', aliases=('退群',))
async def quit_group(session: CommandSession):
    args = session.current_arg_text.split()
    failed = []
    succ = []
    for arg in args:
        if not re.fullmatch(r'^\d+$', arg):
            failed.append(arg)
            continue
        try:
            await session.bot.set_group_leave(self_id=session.event.self_id, group_id=arg)
            succ.append(arg)
        except:
            failed.append(arg)
    msg = f'已尝试退出{len(succ)}个群'
    if failed:
        msg += f"\n失败{len(failed)}个群：{failed}"
    await session.send(msg)
