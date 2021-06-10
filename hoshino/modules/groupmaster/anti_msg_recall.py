from hoshino import Service, util, priv
from hoshino.typing import NoticeSession, Message

sv = Service(
    name='anti-msg-recall',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 是否可见
    enable_on_default=True,  # 是否默认启用
    bundle='通用',  # 属于哪一类
    help_="防撤回"  # 帮助文本
)


@sv.on_notice('group_recall')
async def anti_msg_recall(session: NoticeSession):
    uid = session.event.user_id
    if uid == session.event.operator_id:
        data = await session.bot.get_msg(self_id=session.event.self_id, message_id=session.event.message_id)
        cardname = data.get('sender', {}).get('card')
        nickname = data.get('sender', {}).get('nickname')
        name = cardname or nickname or uid
        msg = data.get('message')
        msg = util.filt_message(Message(msg))
        if msg:
            await session.send(f'{name}({uid})撤回了：\n{msg}')
