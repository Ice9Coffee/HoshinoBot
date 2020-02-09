from nonebot import on_notice, NoticeSession


@on_notice('group_decrease.leave')
async def leave_notice(session:NoticeSession):
    await session.send(f"{session.ctx['user_id']}退群了。")
