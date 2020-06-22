import nonebot
from nonebot import on_request, RequestSession
from hoshino import util


cfg = util.load_config(__file__)
vip_group = cfg.get('vip_group', [])

@on_request('group.invite')
async def handle_group_invite(session:RequestSession):
    if session.ctx['user_id'] in nonebot.get_bot().config.SUPERUSERS:
        await session.approve()
    elif session.ctx['group_id'] in vip_group:
        await session.approve()
    else:
        await session.reject(reason='邀请入群请联系维护组')
