import hoshino
from hoshino import Service, priv
from hoshino.typing import CQEvent
from hoshino.util import DailyNumberLimiter

sv_help = '[来杯咖啡] 后接反馈内容 联系维护组'

sv = Service(
    name='_feedback_',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=False,  # 是否可见
    enable_on_default=False,  # 是否默认启用
    bundle='通用',  # 属于哪一类
    help_=sv_help  # 帮助文本
)

_max = 1
lmt = DailyNumberLimiter(_max)
EXCEED_NOTICE = f'您今天已经喝过{_max}杯了，请明早5点后再来！'


@sv.on_prefix('来杯咖啡')
async def feedback(bot, ev: CQEvent):
    uid = ev.user_id
    if not lmt.check(uid):
        await bot.finish(ev, EXCEED_NOTICE, at_sender=True)
    coffee = hoshino.config.SUPERUSERS[0]
    text = str(ev.message).strip()
    if not text:
        await bot.send(ev, "请发送来杯咖啡+您要反馈的内容~", at_sender=True)
    else:
        await bot.send_private_msg(self_id=ev.self_id, user_id=coffee, message=f'Q{uid}@群{ev.group_id}\n{text}')
        await bot.send(ev, f'您的反馈已发送至维护组！\n======\n{text}', at_sender=True)
        lmt.increase(uid)
