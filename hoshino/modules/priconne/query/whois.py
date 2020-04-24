from hoshino.util import FreqLimiter
from ..chara import Chara
from . import sv

from nonebot import MessageSegment
import random

_lmt = FreqLimiter(5)

@sv.on_rex(r'^[谁誰]是\s*(.{1,20})$', normalize=False)
async def _whois(bot, ctx, match):
    uid = ctx['user_id']
    if not _lmt.check(uid):
        await bot.send(ctx, '您查询得太快了，请稍等一会儿', at_sender=True)
        return
    _lmt.start_cd(uid)

    if ctx['group_id'] == 770947581:
        message = ctx['raw_message'].strip('[CQ:at,qq=2156069011]').strip(' ').strip('谁').strip('誰').strip('是')  # 请将QQ号换为自己Bot的
        if message == '龙王':  # 回避已知外部插件的响应
            return
        elif message == 'Ice-Cirno' or message == 'Ice咖啡' or message == '咖啡' or message == '咖啡佬' or message == '星乃她爹' or message == '星乃主人':
            RAINBOW_P = [f'{str(MessageSegment.at(438971718))}佬牛逼',
                         f'{str(MessageSegment.at(438971718))}佬永远滴神',
                         f'我宣布{str(MessageSegment.at(438971718))}佬牛逼',
                         f'我现在宣布{str(MessageSegment.at(438971718))}佬牛逼',
                         f'那我只能说{str(MessageSegment.at(438971718))}佬牛逼了',
                         f'那我不得不说{str(MessageSegment.at(438971718))}佬牛逼了'
                         ]  # 彩虹屁
            await bot.send(ctx, random.choice(RAINBOW_P))
            return
        else:
            pass

    name = match.group(1)
    chara = Chara.fromname(name)
    if chara.id == Chara.UNKNOWN:
        _lmt.start_cd(uid, 600)
        await bot.send(ctx, f'兰德索尔似乎没有叫"{name}"的人\n角色别称补全计划：github.com/Ice-Cirno/HoshinoBot/issues/5\n您的下次查询将于10分钟后可用', at_sender=True)
        return

    msg = f'{chara.icon.cqcode} {chara.name}'
    await bot.send(ctx, msg, at_sender=True)
