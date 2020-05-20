from nonebot import on_request, RequestSession
from hoshino.util import load_config

''' Config Example
{
    ...,
    "group_approve": {
        "123456": {
            "keywords": ["key1", "key2", "key3"],
            "reject_when_not_match": true/false
        }
    }
}
'''

@on_request('group.add')
async def group_approve(session:RequestSession):
    cfg = load_config(__file__)
    cfg = cfg.get('group_approve', {})
    gid = str(session.event.group_id)
    if gid not in cfg:
        return
    key = cfg[gid].get('keywords', [])
    for k in key:
        if k in session.event.comment:
            await session.approve()
            return
    if cfg[gid].get('reject_when_not_match', False):
        await session.reject()
        return
