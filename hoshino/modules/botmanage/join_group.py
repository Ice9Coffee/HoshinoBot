import nonebot
from nonebot import on_request, RequestSession


@on_request('group.invite')
async def handle_group_invite(session:RequestSession):
    if session.ctx['user_id'] in nonebot.get_bot().config.SUPERUSERS:
        await session.approve()
    else:
        await session.reject(reason='邀请入群请联系维护组')
