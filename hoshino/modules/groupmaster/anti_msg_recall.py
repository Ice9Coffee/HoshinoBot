from hoshino import Service, util
from hoshino.typing import NoticeSession, Message

sv = Service('anti-msg-recall', help_='防撤回', enable_on_default=False)

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
