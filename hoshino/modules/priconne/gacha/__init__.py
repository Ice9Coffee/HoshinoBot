import pytz
from datetime import datetime, timedelta
from collections import defaultdict

from nonebot import get_bot
from nonebot import CommandSession, MessageSegment

from hoshino.util import silence, concat_pic, pic2b64
from hoshino.service import Service

from .gacha import Gacha
from ..chara import Chara


__plugin_name__ = 'gacha'
sv = Service('gacha')
_last_gacha_day = -1
_user_gacha_count = defaultdict(int)    # {user: gacha_count}
_max_gacha_per_day = 5


gacha_10_aliases = ('十连', '十连！', '十连抽', '来个十连', '来发十连', '来次十连', '抽个十连', '抽发十连', '抽次十连', '十连扭蛋', '扭蛋十连',
                    '10连', '10连！', '10连抽', '来个10连', '来发10连', '来次10连', '抽个10连', '抽发10连', '抽次10连', '10连扭蛋', '扭蛋10连',
                    '十連', '十連！', '十連抽', '來個十連', '來發十連', '來次十連', '抽個十連', '抽發十連', '抽次十連', '十連轉蛋', '轉蛋十連',
                    '10連', '10連！', '10連抽', '來個10連', '來發10連', '來次10連', '抽個10連', '抽發10連', '抽次10連', '10連轉蛋', '轉蛋10連')
gacha_1_aliases = ('单抽', '单抽！', '来发单抽', '来个单抽', '来次单抽', '扭蛋单抽', '单抽扭蛋',
                   '單抽', '單抽！', '來發單抽', '來個單抽', '來次單抽', '轉蛋單抽', '單抽轉蛋')

GACHA_DISABLE_NOTICE = '本群转蛋功能已禁用\n使用【启用 gacha】以启用\n（需群管理）'
GACHA_EXCEED_NOTICE = f'您今天已经抽过{_max_gacha_per_day * 1500}钻了，欢迎明天再来！'


def check_gacha_num(user_id):
    global _last_gacha_day, _user_gacha_count
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    day = (now - timedelta(hours=5)).day
    if day != _last_gacha_day:
        _last_gacha_day = day
        _user_gacha_count.clear()
    return bool(_user_gacha_count[user_id] < _max_gacha_per_day)


@sv.on_command('gacha_1', deny_tip=GACHA_DISABLE_NOTICE, aliases=gacha_1_aliases, only_to_me=True)
async def gacha_1(session:CommandSession):
    uid = session.ctx['user_id']
    at = str(MessageSegment.at(session.ctx['user_id']))

    if not check_gacha_num(uid):
        await session.finish(f'{at} {GACHA_EXCEED_NOTICE}')
    _user_gacha_count[uid] += 0.1

    gacha = Gacha()
    chara, hiishi = gacha.gacha_one(gacha.up_prob, gacha.s3_prob, gacha.s2_prob)
    silence_time = hiishi * 60

    res = f'{chara.name} {"★"*chara.star}'
    if get_bot().config.IS_CQPRO:
        res = f'{chara.icon.cqcode} {res}'

    await silence(session.ctx, silence_time)
    msg = f'{at}\n素敵な仲間が増えますよ！\n{res}'
    await session.send(msg)


@sv.on_command('gacha_10', deny_tip=GACHA_DISABLE_NOTICE, aliases=gacha_10_aliases, only_to_me=True)
async def gacha_10(session:CommandSession):
    SUPER_LUCKY_LINE = 170
    uid = session.ctx['user_id']
    at = str(MessageSegment.at(session.ctx['user_id']))

    if not check_gacha_num(uid):
        await session.finish(f'{at} {GACHA_EXCEED_NOTICE}')
    _user_gacha_count[uid] += 1
    
    gacha = Gacha()
    result, hiishi = gacha.gacha_ten()
    silence_time = hiishi * 6 if hiishi < SUPER_LUCKY_LINE else hiishi * 60

    if get_bot().config.IS_CQPRO: 
        res1 = Chara.gen_team_pic(result[ :5], star_slot_verbose=False)
        res2 = Chara.gen_team_pic(result[5: ], star_slot_verbose=False)
        res = concat_pic([res1, res2])
        res = pic2b64(res)
        res = MessageSegment.image(res)
        result = [ f'{c.name}{"★"*c.star}' for c in result]
        res1 = ' '.join(result[0:5])
        res2 = ' '.join(result[5: ])
        res = res + f'{res1}\n{res2}'
    else:
        result = [ f'{c.name}{"★"*c.star}' for c in result]
        res1 = ' '.join(result[0:5])
        res2 = ' '.join(result[5: ])
        res = f'{res1}\n{res2}'

    await silence(session.ctx, silence_time)
    msg = f'{at}\n素敵な仲間が増えますよ！\n{res}'
    await session.send(msg)
    if hiishi >= SUPER_LUCKY_LINE:
        await session.send('恭喜海豹！おめでとうございます！')


@sv.on_command('卡池资讯', deny_tip=GACHA_DISABLE_NOTICE, aliases=('查看卡池', '看看卡池', '康康卡池', '卡池資訊'), only_to_me=False)
async def gacha_info(session:CommandSession):
    gacha = Gacha()
    up_chara = gacha.up
    if get_bot().config.IS_CQPRO: 
        up_chara = map(lambda x: str(Chara.fromname(x).icon.cqcode) + x, up_chara)
    up_chara = '\n'.join(up_chara)
    await session.send(f"本期卡池主打的角色：\n{up_chara}\nUP角色合计={(gacha.up_prob/10):.1f}% 3星出率={(gacha.s3_prob)/10:.1f}%")
