from nonebot import *
from hoshino import Service, priv

sv_help = '''
- 防止撤回desi~
'''.strip()

sv = Service(
    name='防撤回',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # False隐藏
    enable_on_default=False,  # 是否默认启用
    bundle='通用',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助-防撤回"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


@sv.on_notice('group_recall')
async def anti_(session: NoticeSession):
    uid = session.event['user_id']
    gid = session.event['group_id']
    pid = session.event['operator_id']
    mid = session.event['message_id']
    info = await session.bot.get_login_info()
    self_id = info["user_id"]
    msgs = await session.bot.get_msg(message_id=mid)
    msg = msgs['message']
    user_msg = await session.bot.get_group_member_info(group_id=gid, user_id=uid, no_cache=False)
    at = MessageSegment.at(pid)
    if pid == self_id or uid == self_id:
        return
    name = user_msg['card'] if user_msg['card'] else user_msg['nickname']
    msg = f'{at}撤回了{name}的消息\n>{msg}'
    await session.send(msg)
