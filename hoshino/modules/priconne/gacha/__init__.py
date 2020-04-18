import pytz
import random
from datetime import datetime, timedelta
from collections import defaultdict

from nonebot import get_bot
from nonebot import CommandSession, MessageSegment
from nonebot import permission as perm
from hoshino.util import silence, concat_pic, pic2b64
from hoshino.service import Service, Privilege as Priv

from .gacha import Gacha
from ..chara import Chara


__plugin_name__ = 'gacha'
sv = Service('gacha', manage_priv=Priv.SUPERUSER)
_last_gacha_day = -1
_user_jewel_used = defaultdict(int)    # {user: jewel_used}
_max_jewel_per_day = 7500


gacha_10_aliases = ('十连', '十连！', '十连抽', '来个十连', '来发十连', '来次十连', '抽个十连', '抽发十连', '抽次十连', '十连扭蛋', '扭蛋十连',
                    '10连', '10连！', '10连抽', '来个10连', '来发10连', '来次10连', '抽个10连', '抽发10连', '抽次10连', '10连扭蛋', '扭蛋10连',
                    '十連', '十連！', '十連抽', '來個十連', '來發十連', '來次十連', '抽個十連', '抽發十連', '抽次十連', '十連轉蛋', '轉蛋十連',
                    '10連', '10連！', '10連抽', '來個10連', '來發10連', '來次10連', '抽個10連', '抽發10連', '抽次10連', '10連轉蛋', '轉蛋10連')
gacha_1_aliases = ('单抽', '单抽！', '来发单抽', '来个单抽', '来次单抽', '扭蛋单抽', '单抽扭蛋',
                   '單抽', '單抽！', '來發單抽', '來個單抽', '來次單抽', '轉蛋單抽', '單抽轉蛋')
gacha_300_aliases = ('抽一井', '来一井', '来发井', '抽发井', '天井扭蛋', '扭蛋天井', '天井轉蛋', '轉蛋天井')

GACHA_DISABLE_NOTICE = '本群转蛋功能已禁用\n如欲开启，请与维护组联系'
GACHA_EXCEED_NOTICE = '您今天已经抽过{}了，欢迎明早5点后再来！'


@sv.on_command('卡池资讯', deny_tip=GACHA_DISABLE_NOTICE, aliases=('查看卡池', '看看卡池', '康康卡池', '卡池資訊'), only_to_me=False)
async def gacha_info(session:CommandSession):
    gacha = Gacha()
    up_chara = gacha.up
    if get_bot().config.IS_CQPRO: 
        up_chara = map(lambda x: str(Chara.fromname(x).icon.cqcode) + x, up_chara)
    up_chara = '\n'.join(up_chara)
    await session.send(f"本期卡池主打的角色：\n{up_chara}\nUP角色合计={(gacha.up_prob/10):.1f}% 3星出率={(gacha.s3_prob)/10:.1f}%")


async def check_gacha_num(session):
    global _last_gacha_day, _user_jewel_used
    user_id = session.ctx['user_id']
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    day = (now - timedelta(hours=5)).day
    if day != _last_gacha_day:
        _last_gacha_day = day
        _user_jewel_used.clear()
    jewel_used = _user_jewel_used[user_id]
    if jewel_used < _max_jewel_per_day:
        return
    await session.finish(GACHA_EXCEED_NOTICE.format('一井' if jewel_used >= 45000 else f'{jewel_used}钻'), at_sender=True)


@sv.on_command('gacha_1', deny_tip=GACHA_DISABLE_NOTICE, aliases=gacha_1_aliases, only_to_me=True)
async def gacha_1(session:CommandSession):
    
    await check_gacha_num(session)
    uid = session.ctx['user_id']
    _user_jewel_used[uid] += 150
    
    gacha = Gacha()
    chara, hiishi = gacha.gacha_one(gacha.up_prob, gacha.s3_prob, gacha.s2_prob)
    silence_time = hiishi * 60

    res = f'{chara.name} {"★"*chara.star}'
    if get_bot().config.IS_CQPRO:
        res = f'{chara.icon.cqcode} {res}'

    await silence(session.ctx, silence_time)
    await session.send(f'素敵な仲間が増えますよ！\n{res}', at_sender=True)


@sv.on_command('gacha_10', deny_tip=GACHA_DISABLE_NOTICE, aliases=gacha_10_aliases, only_to_me=True)
async def gacha_10(session:CommandSession):
    
    SUPER_LUCKY_LINE = 170
    await check_gacha_num(session)
    uid = session.ctx['user_id']
    _user_jewel_used[uid] += 1500
    
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
    if hiishi >= SUPER_LUCKY_LINE:
        await session.send('恭喜海豹！おめでとうございます！')
    await session.send(f'素敵な仲間が増えますよ！\n{res}', at_sender=True)


@sv.on_command('gacha_300', deny_tip=GACHA_DISABLE_NOTICE, aliases=gacha_300_aliases, only_to_me=True)
async def gacha_300(session:CommandSession):
    
    await check_gacha_num(session)
    uid = session.ctx['user_id']
    _user_jewel_used[uid] += 45000
    
    gacha = Gacha()
    result = gacha.gacha_tenjou()
    up = len(result['up'])
    s3 = len(result['s3'])
    s2 = len(result['s2'])
    s1 = len(result['s1'])
    
    res = [*(result['up']), *(result['s3'])]
    random.shuffle(res)
    lenth = len(res)
    if lenth <= 0:
        res = "竟...竟然没有3★？！"
    else:
        step = 4
        pics = []
        for i in range(0, lenth, step):
            j = min(lenth, i + step)
            pics.append(Chara.gen_team_pic(res[i:j], star_slot_verbose=False))
        res = concat_pic(pics)
        res = pic2b64(res)
        res = MessageSegment.image(res)

    msg = [
        "素敵な仲間が増えますよ！",
        str(res),
        f"共计{up+s3}个3★，{s2}个2★，{s1}个1★",
        f"获得{100*up}个记忆碎片与{50*(up+s3) + 10*s2 + s1}个女神秘石！\n第{result['first_up_pos']}抽首次获得up角色" if up else f"获得{50*(up+s3) + 10*s2 + s1}个女神秘石！"
    ]
    
    if up == 0 and s3 == 0:
        msg.append("太惨了，咱们还是退款删游吧...")
    elif up == 0 and s3 > 7:
        msg.append("up呢？我的up呢？")
    elif up == 0 and s3 <= 3:
        msg.append("这位酋长，梦幻包考虑一下？")
    elif up == 0:
        msg.append("据说天井的概率只有12.16%")
    elif up <= 2:
        if result['first_up_pos'] < 50:
            msg.append("你的喜悦我收到了，滚去喂鲨鱼吧！")
        elif result['first_up_pos'] < 100:
            msg.append("已经可以了，您已经很欧了")
        elif result['first_up_pos'] > 290:
            msg.append("标 准 结 局")
        elif result['first_up_pos'] > 250:
            msg.append("补井还是不补井，这是一个问题...")
        else:
            msg.append("期望之内，亚洲水平")
    elif up == 3:
        msg.append("抽井母五一气呵成！多出30等专武～")
    elif up >= 4:
        msg.append("记忆碎片一大堆！您是托吧？")
    
    silence_time = (100*up + 50*(up+s3) + 10*s2 + s1) * 1
    await silence(session.ctx, silence_time)
    await session.send('\n'.join(msg), at_sender=True)


@sv.on_command('氪金', permission=perm.SUPERUSER, only_to_me=False)
async def kakin(session:CommandSession):
    count = 0
    for m in session.ctx['message']:
        if m.type == 'at' and m.data['qq'] != 'all':
            _user_jewel_used[int(m.data['qq'])] = 0
            count += 1
    if count:
        await session.send(f"已为{count}位用户充值完毕！谢谢惠顾～")
