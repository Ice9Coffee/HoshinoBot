import os
import random
from collections import defaultdict

from hoshino import Service, priv, util
from hoshino.typing import *
from hoshino.util import DailyNumberLimiter, concat_pic, pic2b64, silence

from .. import chara
from .gacha import Gacha

try:
    import ujson as json
except:
    import json


sv_help = '''
[星乃来发十连] 转蛋模拟
[星乃来发单抽] 转蛋模拟
[星乃来一井] 4w5钻！
[查看卡池] 模拟卡池&出率
[切换卡池] 更换模拟卡池
'''.strip()
sv = Service('gacha', help_=sv_help, bundle='pcr娱乐')
jewel_limit = DailyNumberLimiter(6000)
tenjo_limit = DailyNumberLimiter(1)

JEWEL_EXCEED_NOTICE = f'您今天已经抽过{jewel_limit.max}钻了，欢迎明早5点后再来！'
TENJO_EXCEED_NOTICE = f'您今天已经抽过{tenjo_limit.max}张天井券了，欢迎明早5点后再来！'
POOL = ('MIX', 'JP', 'TW', 'BL')
DEFAULT_POOL = POOL[0]

_pool_config_file = os.path.expanduser('~/.hoshino/group_pool_config.json')
_group_pool = {}
try:
    with open(_pool_config_file, encoding='utf8') as f:
        _group_pool = json.load(f)
except FileNotFoundError as e:
    sv.logger.warning('group_pool_config.json not found, will create when needed.')
_group_pool = defaultdict(lambda: DEFAULT_POOL, _group_pool)

def dump_pool_config():
    with open(_pool_config_file, 'w', encoding='utf8') as f:
        json.dump(_group_pool, f, ensure_ascii=False)


gacha_10_aliases = ('抽十连', '十连', '十连！', '十连抽', '来个十连', '来发十连', '来次十连', '抽个十连', '抽发十连', '抽次十连', '十连扭蛋', '扭蛋十连',
                    '10连', '10连！', '10连抽', '来个10连', '来发10连', '来次10连', '抽个10连', '抽发10连', '抽次10连', '10连扭蛋', '扭蛋10连')
gacha_1_aliases = ('单抽', '单抽！', '来发单抽', '来个单抽', '来次单抽', '扭蛋单抽', '单抽扭蛋')
gacha_tenjou_aliases = ('抽一井', '来一井', '来发井', '抽发井', '天井扭蛋', '扭蛋天井')

@sv.on_fullmatch('卡池资讯', '查看卡池', '看看卡池', '康康卡池', '看看up', '看看UP')
async def gacha_info(bot, ev: CQEvent):
    gid = str(ev.group_id)
    gacha = Gacha(_group_pool[gid])
    up_chara = []
    for x in gacha.up:
        icon = await chara.fromname(x, star=3).get_icon()
        up_chara.append(str(icon.cqcode) + x)
    up_chara = '\n'.join(up_chara)
    await bot.send(ev, f"本期卡池主打的角色：\n{up_chara}\nUP角色合计={(gacha.up_prob/10):.1f}% 3★出率={(gacha.s3_prob)/10:.1f}%")


POOL_NAME_TIP = '请选择以下卡池\n> 切换卡池jp\n> 切换卡池tw\n> 切换卡池b\n> 切换卡池mix'
@sv.on_prefix('切换卡池', '选择卡池')
async def set_pool(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能切换卡池', at_sender=True)
    name = util.normalize_str(ev.message.extract_plain_text())
    if not name:
        await bot.finish(ev, POOL_NAME_TIP, at_sender=True)
    elif name in ('国', '国服', 'cn'):
        await bot.finish(ev, '请选择以下卡池\n> 选择卡池 b服\n> 选择卡池 台服')
    elif name in ('b', 'b服', 'bl', 'bilibili'):
        name = 'BL'
    elif name in ('台', '台服', 'tw', 'sonet'):
        name = 'TW'
    elif name in ('日', '日服', 'jp', 'cy', 'cygames'):
        name = 'JP'
    elif name in ('混', '混合', 'mix'):
        name = 'MIX'
    else:
        await bot.finish(ev, f'未知服务器地区 {POOL_NAME_TIP}', at_sender=True)
    gid = str(ev.group_id)
    _group_pool[gid] = name
    dump_pool_config()
    await bot.send(ev, f'卡池已切换为{name}池', at_sender=True)
    await gacha_info(bot, ev)


async def check_jewel_num(bot, ev: CQEvent):
    if not jewel_limit.check(ev.user_id):
        await bot.finish(ev, JEWEL_EXCEED_NOTICE, at_sender=True)


async def check_tenjou_num(bot, ev: CQEvent):
    if not tenjo_limit.check(ev.user_id):
        await bot.finish(ev, TENJO_EXCEED_NOTICE, at_sender=True)


@sv.on_prefix(gacha_1_aliases, only_to_me=True)
async def gacha_1(bot, ev: CQEvent):

    await check_jewel_num(bot, ev)
    jewel_limit.increase(ev.user_id, 150)

    gid = str(ev.group_id)
    gacha = Gacha(_group_pool[gid])
    chara, hiishi = gacha.gacha_one(gacha.up_prob, gacha.s3_prob, gacha.s2_prob)
    silence_time = hiishi * 60

    res = f'{await chara.get_icon_cqcode()} {chara.name} {"★"*chara.star}'

    await silence(ev, silence_time)
    await bot.send(ev, f'素敵な仲間が増えますよ！\n{res}', at_sender=True)


@sv.on_prefix(gacha_10_aliases, only_to_me=True)
async def gacha_10(bot, ev: CQEvent):
    SUPER_LUCKY_LINE = 170

    await check_jewel_num(bot, ev)
    jewel_limit.increase(ev.user_id, 1500)

    gid = str(ev.group_id)
    gacha = Gacha(_group_pool[gid])
    result, hiishi = gacha.gacha_ten()
    silence_time = hiishi * 6 if hiishi < SUPER_LUCKY_LINE else hiishi * 60

    res1 = await chara.gen_team_pic(result[:5], star_slot_verbose=False)
    res2 = await chara.gen_team_pic(result[5:], star_slot_verbose=False)
    res = concat_pic([res1, res2])
    res = pic2b64(res)
    res = MessageSegment.image(res)
    result = [f'{c.name}{"★"*c.star}' for c in result]
    res1 = ' '.join(result[0:5])
    res2 = ' '.join(result[5:])
    res = f'{res}\n{res1}\n{res2}'
    # 纯文字版
    # result = [f'{c.name}{"★"*c.star}' for c in result]
    # res1 = ' '.join(result[0:5])
    # res2 = ' '.join(result[5:])
    # res = f'{res1}\n{res2}'

    if hiishi >= SUPER_LUCKY_LINE:
        await bot.send(ev, '恭喜海豹！おめでとうございます！')
    await bot.send(ev, f'素敵な仲間が増えますよ！\n{res}\n', at_sender=True)
    await silence(ev, silence_time)


@sv.on_prefix(gacha_tenjou_aliases, only_to_me=True)
async def gacha_tenjou(bot, ev: CQEvent):

    await check_tenjou_num(bot, ev)
    tenjo_limit.increase(ev.user_id)

    gid = str(ev.group_id)
    gacha = Gacha(_group_pool[gid])
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
            pics.append(await chara.gen_team_pic(res[i:j], star_slot_verbose=False))
        res = concat_pic(pics)
        res = pic2b64(res)
        res = MessageSegment.image(res)

    msg = [
        f"\n素敵な仲間が増えますよ！ {res}",
        f"★★★×{up+s3} ★★×{s2} ★×{s1}",
        f"获得记忆碎片×{gacha.memo_pieces*up}与女神秘石×{50*(up+s3) + 10*s2 + s1}！\n第{result['first_up_pos']}抽首次获得up角色" if up else f"获得女神秘石{50*(up+s3) + 10*s2 + s1}个！"
    ]

    if up == 0 and s3 == 0:
        msg.append("太惨了，咱们还是退款删游吧...")
    elif up == 0 and s3 > 7:
        msg.append("up呢？我的up呢？")
    elif up == 0 and s3 <= 3:
        msg.append("这位酋长，梦幻包考虑一下？")
    elif up == 0:
        msg.append("据说天井的概率只有" + gacha.tenjou_rate)
    elif up <= 2:
        if result['first_up_pos'] < 50:
            msg.append("你的喜悦我收到了，滚去喂鲨鱼吧！")
        elif result['first_up_pos'] < 100:
            msg.append("已经可以了，您已经很欧了")
        elif result['first_up_pos'] > gacha.tenjou_line - 10:
            msg.append("标 准 结 局")
        elif result['first_up_pos'] > gacha.tenjou_line - 50:
            msg.append("补井还是不补井，这是一个问题...")
        else:
            msg.append("期望之内，亚洲水平")
    elif up == 3:
        msg.append("抽井母五一气呵成！多出30等专武～")
    elif up >= 4:
        msg.append("记忆碎片一大堆！您是托吧？")

    await bot.send(ev, '\n'.join(msg), at_sender=True)
    silence_time = (100*up + 50*(up+s3) + 10*s2 + s1) * 1
    await silence(ev, silence_time)


@sv.on_prefix('氪金')
async def kakin(bot, ev: CQEvent):
    if ev.user_id not in bot.config.SUPERUSERS:
        return
    count = 0
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = int(m.data['qq'])
            jewel_limit.reset(uid)
            tenjo_limit.reset(uid)
            count += 1
    if count:
        await bot.send(ev, f"已为{count}位用户充值完毕！谢谢惠顾～")
