"""
PCR会战管理命令 v2

猴子也会用的会战管理

命令设计遵循以下原则：
- 中文：降低学习成本
- 唯一：There should be one-- and preferably only one --obvious way to do it.
- 耐草：参数不规范时尽量执行
"""

import os
import ujson as json
from datetime import datetime
from typing import List

from nonebot import NoneBot
from nonebot import MessageSegment as ms
from nonebot.typing import Context_T
from hoshino.service import Privilege as Priv

from . import sv, cb_cmd
from .argparse import ArgParser, ArgHolder, ParseResult
from .argparse.argtype import *
from .battlemaster import BattleMaster
from .exception import *


USAGE_ADD_CLAN = '!建会 N<公会名> S<服务器地区>'
USAGE_ADD_MEMBER = '!入会 N<昵称> (Q<qq号>)'
USAGE_LIST_MEMBER = '!查看成员'

ERROR_CLAN_NOTFOUND = f'公会未初始化：请*群管理*使用【{USAGE_ADD_CLAN}】进行初始化'
ERROR_ZERO_MEMBER = f'公会内无成员：使用【{USAGE_ADD_MEMBER}】以添加'
ERROR_MEMBER_NOTFOUND = f'未找到成员：请使用【{USAGE_ADD_MEMBER}】加入公会'
ERROR_PERMISSION_DENIED = '权限不足：需*群管理*以上权限'


@cb_cmd('建会', ArgParser(usage=USAGE_ADD_CLAN, arg_dict={
        'N': ArgHolder(tip='公会名'),
        'S': ArgHolder(tip='服务器地区', type=server_code)}))
async def add_clan(bot:NoneBot, ctx:Context_T, args:ParseResult):
    
    if not await sv.check_permission(ctx, Priv.ADMIN):
        raise PermissionDeniedError(ERROR_PERMISSION_DENIED)
    
    bm = BattleMaster(ctx['group_id'])
    if bm.has_clan(1):
        bm.mod_clan(1, args.N, args.S)
        await bot.send(ctx, f'公会信息已修改！\n{args.N} {server_name(args.S)}', at_sender=True)
    else:
        bm.add_clan(1, args.N, args.S)
        await bot.send(ctx, f'公会建立成功！{args.N} {server_name(args.S)}', at_sender=True)


@cb_cmd('查看公会', ArgParser('!查看公会'))
async def list_clan(bot:NoneBot, ctx:Context_T, args:ParseResult):
    
    bm = BattleMaster(ctx['group_id'])
    clans = bm.list_clan()
    if len(clans):
        clans = map(lambda x: f"{x['cid']}会：{x['name']} {server_name(x['server'])}", clans)
        msg = '本群公会：\n' + '\n'.join(clans)
        await bot.send(ctx, msg, at_sender=True)
    else:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)


@cb_cmd('入会', ArgParser(usage=USAGE_ADD_MEMBER, arg_dict={
        'N': ArgHolder(tip='昵称'),
        'Q': ArgHolder(tip='qq号', type=int, default=0)}))
async def add_member(bot:NoneBot, ctx:Context_T, args:ParseResult):
    
    bm = BattleMaster(ctx['group_id'])
    clan = bm.get_clan(1)
    if not clan:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)
    
    uid = args.Q or args.at or ctx['user_id']
    if uid != ctx['user_id']:
        if not await sv.check_permission(ctx, Priv.ADMIN):
            raise PermissionDeniedError(ERROR_PERMISSION_DENIED + '才能添加其他人')
        try:    # 尝试获取群员信息，用以检查该成员是否在群中
            await bot.get_group_member_info(self_id=ctx['self_id'], group_id=bm.group, user_id=uid)
        except:
            raise NotFoundError(f'Error: 无法获取群员信息，请检查{uid}是否属于本群')
    
    if bm.has_member(uid, bm.group):
        bm.mod_member(uid, bm.group, args.N, 1)
        await bot.send(ctx, f'成员{ms.at(uid)}昵称已修改为{args.N}')
    else:
        bm.add_member(uid, bm.group, args.N, 1)
        await bot.send(ctx, f"成员{ms.at(uid)}添加成功！欢迎{args.N}加入{clan['name']}")


@cb_cmd(('查看成员', '成员查看'), ArgParser(USAGE_LIST_MEMBER))
async def list_member(bot:NoneBot, ctx:Context_T, args:ParseResult):
    
    bm = BattleMaster(ctx['group_id'])
    clan = bm.get_clan(1)
    if not clan:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)
    
    mems = bm.list_member(1)
    if l := len(mems):
        # 数字太多会被腾讯ban
        mems = map(lambda x: '{uid: <11,d} | {name}'.format_map(x), mems)
        msg = f"{clan['name']}：人数 {l}/30\nQQ | 昵称\n" + '\n'.join(mems)
        await bot.send(ctx, msg, at_sender=True)
    else:
        raise NotFoundError(ERROR_ZERO_MEMBER)

        
@cb_cmd('退会', ArgParser(usage='!退会 (Q<qq号>)', arg_dict={
        'Q': ArgHolder(tip='qq号', type=int, default=0)}))
async def del_member(bot:NoneBot, ctx:Context_T, args:ParseResult):
    
    bm = BattleMaster(ctx['group_id'])
    uid = args.Q or args.at or ctx['user_id']
    mem = bm.get_member(uid, bm.group) or bm.get_member(uid, 0) # 兼容cmdv1
    if not mem:
        raise NotFoundError('公会内无此成员')
    if uid != ctx['user_id']:
        if not await sv.check_permission(ctx, Priv.ADMIN):
            raise PermissionDeniedError(ERROR_PERMISSION_DENIED + '才能踢人')

    bm.del_member(uid, mem['alt'])
    await bot.send(ctx, f"成员{mem['name']}已从公会删除", at_sender=True)


@cb_cmd('清空成员', ArgParser('!清空成员'))
async def clear_member(bot:NoneBot, ctx:Context_T, args:ParseResult):
    
    if not await sv.check_permission(ctx, Priv.ADMIN):
        raise PermissionDeniedError(ERROR_PERMISSION_DENIED)
    
    bm = BattleMaster(ctx['group_id'])
    if not bm.has_clan(1):
        raise NotFoundError(ERROR_CLAN_NOTFOUND)
    msg = '公会已清空！' if bm.clear_member(1) else '公会内无成员'
    await bot.send(ctx, msg, at_sender=True)


@cb_cmd('一键入会', ArgParser('!一键入会'))
async def batch_add_member(bot:NoneBot, ctx:Context_T, args:ParseResult):
    
    if not await sv.check_permission(ctx, Priv.ADMIN):
        raise PermissionDeniedError(ERROR_PERMISSION_DENIED)

    bm = BattleMaster(ctx['group_id'])
    if not bm.has_clan(1):
        raise NotFoundError(ERROR_CLAN_NOTFOUND)

    mlist = await bot.get_group_member_list(group_id=bm.group)
    if len(mlist) > 40:
        raise ClanBattleError('群员过多！一键入会仅限40人以内群使用')
    
    self_id = ctx['self_id']
    succ, fail = 0, 0
    for m in mlist:
        if m['user_id'] != self_id:
            try:
                bm.add_member(m['user_id'], bm.group, m['card'] or m['nickname'] or str(m['user_id']), 1)
                succ += 1
            except DatabaseError:
                fail += 1
    msg = f'批量注册完成！成功{succ}/失败{fail}\n使用【{USAGE_LIST_MEMBER}】查看当前成员列表'
    await bot.send(ctx, msg, at_sender=True)


async def process_challenge(bot:NoneBot, ctx:Context_T, ch:ParseResult):
    """
    处理一条报刀 需要保证challenge['flag']的正确性
    """
    
    bm = BattleMaster(ctx['group_id'])
    now = datetime.now()
    clan = bm.get_clan(1)
    if not clan:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)
    mem = bm.get_member(ch.uid, ch.alt) or bm.get_member(ch.uid, 0) # 兼容cmdv1
    if not mem:
        raise NotFoundError(ERROR_MEMBER_NOTFOUND)
    
    cur_round, cur_boss, cur_hp = bm.get_challenge_progress(1, now)
    round_ = ch.round or cur_round
    boss = ch.boss or cur_boss
    damage = ch.damage if ch.flag != BattleMaster.LAST else (ch.damage or cur_hp)
    flag = ch.flag

    if (ch.flag == BattleMaster.LAST) and (ch.round or ch.boss) and (not damage):
        raise NotFoundError('补报尾刀请给出伤害值')     # 补报尾刀必须给出伤害值

    msg = ['']
    if round_ != cur_round or boss != cur_boss:
        msg.append('⚠️上报与当前进度不一致')
    else:   # 伤害校对
        eps = 30000
        if damage > cur_hp + eps:
            damage = cur_hp
            msg.append('⚠️过度虐杀 伤害数值已自动修正')
            if flag == BattleMaster.NORM:
                flag = BattleMaster.LAST
                msg.append('⚠️已自动标记为尾刀')
        elif flag == BattleMaster.LAST:
            if damage < cur_hp - eps:
                msg.append('⚠️尾刀伤害不足 请未报刀成员及时上报')
            elif damage < cur_hp:
                if damage % 1000 == 0:
                    damage = cur_hp
                    msg.append('⚠️尾刀伤害已自动修正')
                else:
                    msg.append('⚠️Boss仍有少量残留血量')

    eid = bm.add_challenge(mem['uid'], mem['alt'], round_, boss, damage, flag, now)
    aft_round, aft_boss, aft_hp = bm.get_challenge_progress(1, now)
    max_hp, score_rate = bm.get_boss_info(aft_round, aft_boss, clan['server'])
    msg.append(f"记录编号E{eid}：{mem['name']}给予{round_}周目{bm.int2kanji(boss)}王{damage:,d}点伤害")
    msg.append(f"{clan['name']}当前进度：\n{aft_round}周目{aft_boss}王\nHP={aft_hp:,d}/{max_hp:,d}\nSCOREx{score_rate:.1f}")
    await bot.send(ctx, '\n'.join(msg), at_sender=True)

    # 判断是否更换boss，呼叫预约
    if aft_round != cur_round or aft_boss != cur_boss:
        await call_reserve(bot, ctx, aft_round, aft_boss)


@cb_cmd('出刀', ArgParser(usage='!出刀 <伤害值> (Q<qq号>)', arg_dict={
    '': ArgHolder(tip='伤害值', type=damage_int),
    'Q': ArgHolder(tip='qq号', type=int, default=0),
    'R': ArgHolder(tip='周目数', type=round_code, default=0),
    'B': ArgHolder(tip='Boss编号', type=boss_code, default=0)}))    
async def add_challenge(bot:NoneBot, ctx:Context_T, args:ParseResult):
    challenge = ParseResult({
        'round': args.R,
        'boss': args.B,
        'damage': args.get(''),
        'uid': args.Q or args.at or ctx['user_id'],
        'alt': ctx['group_id'],
        'flag': BattleMaster.NORM
    })
    await process_challenge(bot, ctx, challenge)


@cb_cmd(('出尾刀', '收尾'), ArgParser(usage='!出尾刀 (<伤害值>) (Q<qq号>)', arg_dict={
    '': ArgHolder(tip='伤害值', type=damage_int, default=0),
    'Q': ArgHolder(tip='qq号', type=int, default=0),
    'R': ArgHolder(tip='周目数', type=round_code, default=0),
    'B': ArgHolder(tip='Boss编号', type=boss_code, default=0)}))
async def add_challenge_last(bot:NoneBot, ctx:Context_T, args:ParseResult):
    challenge = ParseResult({
        'round': args.R,
        'boss': args.B,
        'damage': args.get(''),
        'uid': args.Q or args.at or ctx['user_id'],
        'alt': ctx['group_id'],
        'flag': BattleMaster.LAST
    })
    await process_challenge(bot, ctx, challenge)


@cb_cmd('出补时刀', ArgParser(usage='!出补时刀 <伤害值> (Q<qq号>)', arg_dict={
    '': ArgHolder(tip='伤害值', type=damage_int),
    'Q': ArgHolder(tip='qq号', type=int, default=0),
    'R': ArgHolder(tip='周目数', type=round_code, default=0),
    'B': ArgHolder(tip='Boss编号', type=boss_code, default=0)}))    
async def add_challenge_ext(bot:NoneBot, ctx:Context_T, args:ParseResult):
    challenge = ParseResult({
        'round': args.R,
        'boss': args.B,
        'damage': args.get(''),
        'uid': args.Q or args.at or ctx['user_id'],
        'alt': ctx['group_id'],
        'flag': BattleMaster.EXT
    })
    await process_challenge(bot, ctx, challenge)


@cb_cmd('掉刀', ArgParser(usage='!掉刀 (Q<qq号>)', arg_dict={
    'Q': ArgHolder(tip='qq号', type=int, default=0),
    'R': ArgHolder(tip='周目数', type=round_code, default=0),
    'B': ArgHolder(tip='Boss编号', type=boss_code, default=0)}))    
async def add_challenge_timeout(bot:NoneBot, ctx:Context_T, args:ParseResult):
    challenge = ParseResult({
        'round': args.R,
        'boss': args.B,
        'damage': 0,
        'uid': args.Q or args.at or ctx['user_id'],
        'alt': ctx['group_id'],
        'flag': BattleMaster.TIMEOUT
    })
    await process_challenge(bot, ctx, challenge)


@cb_cmd('删刀', ArgParser(usage='!删刀 E<记录编号>', arg_dict={
    'E': ArgHolder(tip='记录编号', type=int)}))
async def del_challenge(bot:NoneBot, ctx:Context_T, args:ParseResult):
    bm = BattleMaster(ctx['group_id'])
    now = datetime.now()
    clan = bm.get_clan(1)
    if not clan:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)
    ch = bm.get_challenge(args.E, 1, now)
    if not ch:
        raise NotFoundError(f'未找到出刀记录E{args.E}')
    if ch['uid'] != ctx['user_id']:
        if not await sv.check_permission(ctx, Priv.ADMIN):
            raise PermissionDeniedError(ERROR_PERMISSION_DENIED + '才能删除其他人的记录')
    bm.del_challenge(args.E, 1, now)
    await bot.send(ctx, f"{clan['name']}已删除{ms.at(ch['uid'])}的出刀记录E{args.E}", at_sender=True)


# TODO 将预约信息转至数据库
SUBSCRIBE_PATH = os.path.expanduser('~/.hoshino/clanbattle_sub/')
SUBSCRIBE_MAX = 3
os.makedirs(SUBSCRIBE_PATH, exist_ok=True)

def _load_sub(gid):
    filename = os.path.join(SUBSCRIBE_PATH, f"{gid}.json")
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf8') as f:
            return json.load(f)
    else:
        return {'1':[], '2':[], '3':[], '4':[], '5':[]}


def _save_sub(sub, gid):
    filename = os.path.join(SUBSCRIBE_PATH, f"{gid}.json")
    with open(filename, 'w', encoding='utf8') as f:
        json.dump(sub, f, ensure_ascii=False)


def _gen_sublist_msg(bm:BattleMaster, sublist:List[int]):
    mems = map(lambda x: bm.get_member(x, bm.group) or bm.get_member(x, 0) or {'name': str(x)}, sublist)
    mems = map(lambda x: x['name'], mems)
    return mems


@cb_cmd('预约', ArgParser(usage='!预约 <Boss号>', arg_dict={
    '': ArgHolder(tip='Boss编号', type=boss_code)}))
async def subscribe(bot:NoneBot, ctx:Context_T, args:ParseResult):
    bm = BattleMaster(ctx['group_id'])
    uid = ctx['user_id']
    clan = bm.get_clan(1)
    if not clan:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)
    mem = bm.get_member(uid, bm.group) or bm.get_member(uid, 0)     # 兼容cmdv1
    if not mem:
        raise NotFoundError(ERROR_MEMBER_NOTFOUND)
    
    sub = _load_sub(bm.group)
    boss = args['']
    slist = sub[str(boss)]
    if uid in slist:
        await bot.send(ctx, f'您已经预约过{bm.int2kanji(boss)}王了', at_sender=True)
    elif len(slist) >= SUBSCRIBE_MAX:
        await bot.send(ctx, f'{bm.int2kanji(boss)}王预约人数已达上限：{SUBSCRIBE_MAX} 预约失败', at_sender=True)
    else:
        slist.append(uid)
        _save_sub(sub, bm.group)
        msg = [
            f'已为您预约{bm.int2kanji(boss)}王！',
            f'该Boss当前预约人数：{len(slist)}',
        ]
        msg.extend(_gen_sublist_msg(bm, slist))
        await bot.send(ctx, '\n'.join(msg), at_sender=True)


@cb_cmd(('取消预约', '预约取消'), ArgParser(usage='!取消预约 <Boss号>', arg_dict={
    '': ArgHolder(tip='Boss编号', type=boss_code)}))
async def unsubscribe(bot:NoneBot, ctx:Context_T, args:ParseResult):
    bm = BattleMaster(ctx['group_id'])
    uid = ctx['user_id']
    clan = bm.get_clan(1)
    if not clan:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)
    mem = bm.get_member(uid, bm.group) or bm.get_member(uid, 0)     # 兼容cmdv1
    if not mem:
        raise NotFoundError(ERROR_MEMBER_NOTFOUND)
    
    sub = _load_sub(bm.group)    
    boss = args['']
    slist = sub[str(boss)]
    
    if uid in slist:
        slist.remove(uid)
        _save_sub(sub, bm.group)
        msg = [
            f'已为您取消预约{bm.int2kanji(boss)}王！',
            f'该Boss当前预约人数：{len(slist)}',
        ]
        msg.extend(_gen_sublist_msg(bm, slist))
        await bot.send(ctx, '\n'.join(msg), at_sender=True)


async def call_reserve(bot:NoneBot, ctx:Context_T, round_:int, boss:int):
    sub = _load_sub(ctx['group_id'])
    slist = sub[str(boss)]
    if slist:
        msg = [ f"您们预约的老{BattleMaster.int2kanji(boss)}出现啦！" ]
        msg.extend(map(lambda x: str(ms.at(x)), slist))
        msg.append("快点出刀！错过本轮重新预约")
        slist.clear()
        await bot.send(ctx, '\n'.join(msg))    


@cb_cmd(('查询预约', '预约查询', '查看预约', '预约查看'), ArgParser('!查询预约'))
async def list_subscribe(bot:NoneBot, ctx:Context_T, args:ParseResult):
    bm = BattleMaster(ctx['group_id'])
    clan = bm.get_clan(1)
    if not clan:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)
    msg = [ f"{clan['name']}当前预约情况：" ]
    sub = _load_sub(bm.group)
    for boss in range(1, 6):
        slist = sub[str(boss)]
        msg.append(f"Boss {boss}: {len(slist)}人")
        msg.extend(_gen_sublist_msg(bm, slist))
    await bot.send(ctx, '\n'.join(msg), at_sender=True)



@cb_cmd('进度', ArgParser(usage='!进度'))
async def show_progress(bot:NoneBot, ctx:Context_T, args:ParseResult):
    bm = BattleMaster(ctx['group_id'])
    clan = bm.get_clan(1)
    if not clan:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)
    r, b, hp = bm.get_challenge_progress(1, datetime.now())
    max_hp, score_rate = bm.get_boss_info(r, b, clan['server'])
    msg = f"{clan['name']}当前进度：{r}周目{b}王\nHP={hp:,d}/{max_hp:,d}\nSCOREx{score_rate:.1f}"
    await bot.send(ctx, msg, at_sender=True)


@cb_cmd('统计', ArgParser(usage='!统计'))
async def stat(bot:NoneBot, ctx:Context_T, args:ParseResult):
    bm = BattleMaster(ctx['group_id'])
    now = datetime.now()
    clan = bm.get_clan(1)
    if not clan:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)
    yyyy, mm, _ = bm.get_yyyymmdd(now)
    msg = [ f"{yyyy}年{mm}月会战{clan['name']}分数统计：" ]
    stat = bm.stat_score(1, now)
    stat.sort(key=lambda x: x[3], reverse=True)
    for _, _, name, score in stat:
        score = f'{score:,d}'           # 数字太多会被腾讯ban，用逗号分隔
        blank = '  ' * (11-len(score))  # QQ字体非等宽，width(空格*2) == width(数字*1)
        msg.append(f"{blank}{score}分 | {name}")
    await bot.send(ctx, '\n'.join(msg), at_sender=True)


async def _do_show_remain(bot:NoneBot, ctx:Context_T, args:ParseResult, at_user:bool):
    bm = BattleMaster(ctx['group_id'])
    clan = bm.get_clan(1)
    if not clan:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)
    if at_user and not await sv.check_permission(ctx, Priv.ADMIN):
        raise PermissionDeniedError(ERROR_PERMISSION_DENIED + '才能催刀。您可以用【!查刀】查询余刀')
    rlist = bm.list_challenge_remain(1, datetime.now())
    rlist.sort(key=lambda x: x[3] + x[4], reverse=True)
    msg = [ f"{clan['name']}今日余刀：" ]
    for uid, _, name, r_n, r_e in rlist:
        if r_n or r_e:
            line = f"{ms.at(uid) if at_user else name} 剩"
            if r_n:
                line += f" {r_n}正常刀"
            if r_e:
                line += f" {r_e}补时刀"
            msg.append(line)
    if len(msg) == 1:
        await bot.send(ctx, f"今日{clan['name']}所有成员均已下班！各位辛苦了！", at_sender=True)
    else:
        msg.append("负数说明报刀有误 请注意核对")
        if at_user:
            msg.append("=========\n在？阿sir喊你出刀啦！")
        await bot.send(ctx, '\n'.join(msg), at_sender=True)


@cb_cmd('查刀', ArgParser(usage='!查刀'))
async def list_remain(bot:NoneBot, ctx:Context_T, args:ParseResult):
    await _do_show_remain(bot, ctx, args, at_user=False)
@cb_cmd('催刀', ArgParser(usage='!催刀'))
async def urge_remain(bot:NoneBot, ctx:Context_T, args:ParseResult):
    await _do_show_remain(bot, ctx, args, at_user=False)

