from nonebot import on_command, CommandSession, permission as perm
from hoshino.util import DailyNumberLimiter

_max = 1
_lmt = DailyNumberLimiter(_max)
EXCEED_NOTICE = f'您今天已经喝过{_max}杯了，请明早5点后再来！'

@on_command('来杯咖啡', permission=perm.GROUP)
async def feedback(session:CommandSession):
    uid = session.ctx['user_id']
    if not _lmt.check(uid):
        session.finish(EXCEED_NOTICE, at_sender=True)
    coffee = session.bot.config.SUPERUSERS[0]
    text = session.current_arg
    if not text:
        await session.send(f"来杯咖啡[空格]后输入您要反馈的内容~", at_sender=True)
    else:
        await session.bot.send_private_msg(self_id=session.ctx['self_id'], user_id=coffee, message=f'Q{uid}@群{session.ctx["group_id"]}\n{text}')
        await session.send(f'您的反馈已发送！\n=======\n{text}', at_sender=True)
        _lmt.increase(uid)
