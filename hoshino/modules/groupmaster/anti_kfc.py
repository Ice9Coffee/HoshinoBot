import itertools
from datetime import timedelta
from hoshino import Service, priv, util
from hoshino.typing import CQEvent, CQHttpError, MessageSegment as ms

sv = Service('anti-kfc', enable_on_default=False)

CRAZY_THURSDAY_ALIAS = list(map(''.join, itertools.product(('疯狂', '狂乱'), ('星期四', '木曜日', '星期寺'))))
THURSDAY_ALIAS = ['⭐期四', '⭐期4']
VME50_ALIAS = list(map(''.join, itertools.product(
    ('v', 'give', '给', '送', '微', 'send', 'transfer', 'vi'),
    ('', ' '),
    ('', '我', '卧', '窝', '窩', '沃', '在下', '朕', '孤', '私', '俺', '僕', '咱', 'me', 'i', 'w', 'wo', 'vo'),
    ('', ' '),
    ('五', '50', '5十', '5百', 'five', 'fifty', 'half 100', 'half100', 'half百', 'half1百', 'half 1百'),
)))


@sv.on_keyword(
    'kfc', '肯德基', '肯德鸡', '肯德🐓', '肯德🐔',
    *CRAZY_THURSDAY_ALIAS,
    *THURSDAY_ALIAS)
async def anti_kfc_crazy_thursday(bot, ev: CQEvent):
    priv.set_block_user(ev.user_id, timedelta(seconds=240))
    await util.silence(ev, 4 * 60, skip_su=False)
    await bot.send(ev, f'{ms.at(ev.user_id)} 本群正在对美实施经济制裁，本周不参加疯狂星期四！')
    try:
        await bot.delete_msg(self_id=ev.self_id, message_id=ev.message_id)
    except CQHttpError:
        pass


@sv.on_keyword(*VME50_ALIAS)
async def anti_vme50(bot, ev: CQEvent):
    priv.set_block_user(ev.user_id, timedelta(seconds=240))
    await util.silence(ev, 4 * 60, skip_su=False)
    await bot.send(ev, f'{ms.at(ev.user_id)} 反诈中心星乃分部提醒您：以疯狂星期四等名义向您索要钱财的均为诈骗！')
    # try:
    #     await bot.delete_msg(self_id=ev.self_id, message_id=ev.message_id)
    # except CQHttpError:
    #     pass
