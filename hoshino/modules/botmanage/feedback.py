import pytz
from datetime import datetime, timedelta
from collections import defaultdict

from nonebot import on_command, CommandSession, MessageSegment
import nonebot.permission as perm

_last_coffee_day = -1
_user_coffee_count = defaultdict(int)    # {user: coffee_count}
_max_coffee_per_day = 1
COFFEE_EXCEED_NOTICE = f'您今天已经喝过{_max_coffee_per_day}杯了，请明早5点后再来！'

def check_coffee_num(user_id):
    global _last_coffee_day, _user_coffee_count, _max_coffee_per_day
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    day = (now - timedelta(hours=5)).day
    if day != _last_coffee_day:
        _last_coffee_day = day
        _user_coffee_count.clear()
    return bool(_user_coffee_count[user_id] < _max_coffee_per_day)


@on_command('来杯咖啡', permission=perm.GROUP)
async def feedback(session:CommandSession):
    uid = session.ctx['user_id']
    if not check_coffee_num(uid):
        await session.send(COFFEE_EXCEED_NOTICE, at_sender=True)
        return

    coffee = session.bot.config.SUPERUSERS[0]
    text = session.current_arg
    if not text:
        await session.send(f"来杯咖啡[空格]后输入您要反馈的内容~", at_sender=True)
    else:
        await session.bot.send_private_msg(self_id=session.ctx['self_id'], user_id=coffee, message=f'Q{uid}@群{session.ctx["group_id"]}\n{text}')
        await session.send(f'您的反馈已发送！\n=======\n{text}', at_sender=True)
        _user_coffee_count[uid] += 1
