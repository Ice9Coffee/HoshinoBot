
import hoshino
from hoshino import Service
from hoshino.typing import NoticeSession

sv1 = Service('group-leave-notice', help_='退群通知')

@sv1.on_notice('group_decrease.leave')
async def leave_notice(session: NoticeSession):
    await session.send(f"{session.ctx['user_id']}退群了。")


sv2 = Service('group-welcome', help_='入群欢迎')

@sv2.on_notice('group_increase')
async def increace_welcome(session: NoticeSession):
    
    if session.event.user_id == session.event.self_id:
        return  # ignore myself
    
    welcomes = hoshino.config.groupmaster.increase_welcome
    gid = session.event.group_id
    if gid in welcomes:
        await session.send(welcomes[gid], at_sender=True)
    # elif 'default' in welcomes:
    #     await session.send(welcomes['default'], at_sender=True)
