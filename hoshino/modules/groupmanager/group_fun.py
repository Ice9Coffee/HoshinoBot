from hoshino import Service, priv, R
from hoshino.util import DailyNumberLimiter

import random

from . import util

sv_help = '''
- [谁是龙王] 迫害龙王
- [@bot 送礼物@sb] 让bot送sb礼物
- [@bot 饿饿] 让bot送自己礼物
- [说 XX] bot说xx
'''.strip()

sv = Service(
    name='群管plus',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # False隐藏
    enable_on_default=True,  # 是否默认启用
    bundle='通用',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助-群管plus"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


@sv.on_fullmatch(('谁是龙王', '迫害龙王', '龙王是谁'))
async def whois_dragon_king(bot, ev):
    gid = ev.group_id
    img_path = R.img('longwang/').path  # 随机龙王图开始
    filename = random.choice(img_path)
    pic = R.img('longwang/', filename).cqcode  # 随机龙王图结束
    self_info = await util.self_member_info(bot, ev, gid)
    sid = self_info['user_id']
    honor_type = 'talkative'
    ta_info = await util.honor_info(bot, ev, gid, honor_type)
    if 'current_talkative' not in ta_info:
        await bot.send(ev, '本群没有开启龙王标志哦~')
        return
    dk = ta_info['current_talkative']['user_id']
    if sid == dk:
        await bot.send(ev, f'啊，我是龙王\n{pic}')
    else:
        action = random.choice(['龙王出来挨透', '龙王出来喷水'])
        dk_avater = ta_info['current_talkative']['avatar'] + '640' + f'&t={dk}'
        await bot.send(ev, f'[CQ:at,qq={dk}]\n{action}\n[CQ:image,file={dk_avater}]')


'''
@sv.on_prefix(('送礼物','，土豪，我也要礼物~','给我礼物','我要礼物','要礼物','饿饿'),only_to_me=False)
async def send_gift(bot, ev):
    uid = ev.user_id
    sid = None
    gid = ev.group_id
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
        elif m.type == 'at' and m.data['qq'] == 'all':
            await bot.send(ev, '这种事情做不到啦~', at_sender=True)
            return
    if sid is None:
        sid = uid
    await bot.send(ev, f'[CQ:gift,qq={sid},id=1]')
'''
'''
@sv.on_prefix(('点赞','赞我'),only_to_me=False)
async def send_zan(bot, ev):
    uid = ev.user_id
    sid = None
    gid = ev.group_id
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
        elif m.type == 'at' and m.data['qq'] == 'all':
            await bot.send(ev, '这种事情做不到啦~', at_sender=True)
            return
    if sid is None:
        sid = uid
    await bot.send_like(user_id={sid})
 '''


@sv.on_prefix(('说', '跟我说'), only_to_me=True)
async def send_gift(bot, ev):
    uid = ev.user_id
    sid = None
    gid = ev.group_id
    res = str(ev.message.extract_plain_text())
    await bot.send(ev, f'[CQ:tts,text={res}]')


@sv.on_prefix('申请小尾巴')
async def yiba(bot, ev):
    uid = ev.user_id
    sid = None
    gid = ev.group_id
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
    if sid is None:
        sid = uid
    fcode = u'\u202e'
    ecode = u'\u202d'
    kw = ev.message.extract_plain_text().strip()
    weiba = fcode + kw[::-1] + ecode
    info = await bot.get_group_member_info(group_id=gid, user_id=uid, no_cache=True)
    oldcard = info['card'] or info['nickname']
    newcard = oldcard + weiba
    try:
        await util.card_edit(bot, ev, uid, sid, gid, newcard)
    except Exception as e:
        sv.logger.error(e)
        await bot.send(ev, '好像不能亲手给你戴上呢> <，请自己全选复制换上去吧~', at_sender=True)
        await bot.send(ev, newcard)
