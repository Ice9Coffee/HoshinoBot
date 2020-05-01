# 公主连接Re:Dive会战管理插件
# clan == クラン == 戰隊（直译为氏族）（CLANNAD的CLAN（笑））

import json
import os
import re
from datetime import datetime

from nonebot import on_command, CommandSession, MessageSegment
from nonebot import permission as perm
from nonebot.argparse import ArgumentParser

from hoshino.log import logger

from .battlemaster import BattleMaster


def get_digi(x: int):
    '''
    获取非负数x的十进制位数
    '''
    if 0 == x:
        return 1
    ans = 0
    while x > 0:
        ans = ans + 1
        x = x // 10
    return ans


@on_command('add-clan', permission=perm.GROUP, shell_like=True, only_to_me=False)
async def add_clan(session:CommandSession):

    if not await perm.check_permission(session.bot, session.ctx, perm.GROUP_ADMIN):
        await session.finish('Error: 只有管理员才能添加新公会')

    parser = ArgumentParser(session=session, usage='add-clan --name [--cid] --server')
    parser.add_argument('--name', default=None, required=False)
    parser.add_argument('--cid', type=int, default=-1)
    parser.add_argument('--server', default='Unknown')
    args = parser.parse_args(session.argv)
    group_id = session.ctx['group_id']
    battlemaster = BattleMaster(group_id)

    name = args.name
    if not name:
        ginfo = await session.bot._get_group_info(self_id=session.ctx['self_id'], group_id=group_id)
        name = ginfo['group_name']

    cid = args.cid
    if cid <= 0:
        clans = battlemaster.list_clan()
        for clan in clans:
            cid = clan['cid'] if clan['cid'] > cid else cid
        cid = cid + 1 if cid > 0 else 1

    server = battlemaster.get_server_code(args.server)
    if server < 0:
        await session.finish('请指定公会所在服务器 例【add-clan --server jp】')

    if battlemaster.add_clan(cid, name, server):
        await session.send('公会添加失败...ごめんなさい！嘤嘤嘤(〒︿〒)')
    else:
        await session.send(f'公会添加成功！{cid}会 {name}')


@on_command('list-clan', permission=perm.GROUP, only_to_me=False)
async def list_clan(session: CommandSession):
    battlemaster = BattleMaster(session.ctx['group_id'])
    clans = battlemaster.list_clan()
    if len(clans):
        msg = '本群公会一览：\n'
        clanstr = '{cid}会：{name}\n'
        for clan in clans:
            msg = msg + clanstr.format_map(clan)
        await session.send(msg)
    else:
        await session.send('本群目前没有公会哟')


@on_command('add-member', aliases=('join-clan', ), permission=perm.GROUP, shell_like=True, only_to_me=False)
async def add_member(session: CommandSession):
    parser = ArgumentParser(session=session, usage='add-member [--cid] [--uid] [--alt] [--name]\n\n加入1会:\n【 join-clan --name [游戏内昵称（缺省自动获取群名片）] 】\n将骑士A的小号2加入3会：\n【 add-member --uid [骑士A的QQ号] --alt 2 --cid 3 --name [骑士A的昵称] 】')
    parser.add_argument('--cid', type=int, default=1)
    parser.add_argument('--uid', type=int, default=-1)
    parser.add_argument('--alt', type=int, default=0)
    parser.add_argument('--name', default=None)
    args = parser.parse_args(session.argv)

    group_id = session.ctx['group_id']
    cid = args.cid
    uid = args.uid if args.uid > 0 else session.ctx['user_id']
    alt = args.alt
    name = args.name
    try:    # 尝试获取群员信息，用以检查该成员是否在群中
        group_member_info = await session.bot.get_group_member_info(self_id=session.ctx['self_id'], group_id=group_id, user_id=uid)
    except:
        await session.finish(f'Error: 无法获取到指定群员的信息，请检查{uid}是否属于本群\n（注：uid为QQ号，机器人无需九码，如有小号请指定alt参数）')
        return
    if not name:
        name = group_member_info['card']
        if not name.strip():
            session.finish('Error: name参数未指定，且获取群名片为空。请尝试指定name参数（建议使用游戏内昵称）')


    battlemaster = BattleMaster(group_id)
    clan = battlemaster.get_clan(cid)
    if not clan:
        await session.finish(f'Error: 指定的分会{cid}不存在')
    if alt < 0:
        await session.finish('Error: 小号编号不能小于0')
    if uid != session.ctx['user_id']:
        if not await perm.check_permission(session.bot, session.ctx, perm.GROUP_ADMIN):
            await session.finish('Error: 只有管理员才能添加其他人到公会')


    if battlemaster.add_member(uid, alt, name, cid):
        await session.send(f'成员添加失败...ごめんなさい！嘤嘤嘤(〒︿〒)\n请检查账号{uid}（的小号{alt}）是否已存在于其他公会')
    else:
        msg_alt = f'的{alt}号小号' if alt else ''
        clan_name = clan['name']
        await session.send(f'成员添加成功！欢迎{name}{msg_alt}加入{cid}会 {clan_name}')


@on_command('list-member', permission=perm.GROUP, shell_like=True, only_to_me=False)
async def list_member(session: CommandSession):
    parser = ArgumentParser(session=session, usage='list-member [--cid]')
    parser.add_argument('--cid', type=int, default=1)
    args = parser.parse_args(session.argv)
    
    group_id = session.ctx['group_id']
    cid = args.cid

    battlemaster = BattleMaster(group_id)
    clan = battlemaster.get_clan(cid)

    if not clan:
        await session.finish('Error: 指定的分会不存在')
    cmems = battlemaster.list_member(cid)
    if len(cmems):
        msg = f'{cid}会成员一览：  {len(cmems)}/30\nQQ|name\n'
        # 数字太多会被腾讯ban
        memstr = '{uid: <11,d} {name}\n'
        memstr_alt = '{uid: <11,d} {name} 小号{alt}\n'

        for m in cmems:
            msg = msg + (memstr.format_map(m) if not m['alt'] else memstr_alt.format_map(m))
        await session.send(msg)
    else:
        await session.send(f'{cid}会目前还没有成员')


@on_command('del-member', aliases=('quit-clan', ), permission=perm.GROUP, shell_like=True, only_to_me=False)
async def del_member(session: CommandSession):
    parser = ArgumentParser(session=session, usage='del-member [--uid] [--alt]')
    parser.add_argument('--uid', type=int, default=-1)
    parser.add_argument('--alt', type=int, default=0)
    args = parser.parse_args(session.argv)

    group_id = session.ctx['group_id']
    uid = args.uid if args.uid > 0 else session.ctx['user_id']
    alt = args.alt

    battlemaster = BattleMaster(group_id)

    mem = battlemaster.get_member(uid, alt)

    if mem == None:
        await session.finish('Error: 指定成员不在本群')

    if uid != session.ctx['user_id']:
        if not await perm.check_permission(session.bot, session.ctx, perm.GROUP_ADMIN):
            await session.finish('Error: 只有管理员才能删除其他成员')

    if battlemaster.del_member(uid, alt):
        await session.send('成员删除失败...ごめんなさい！嘤嘤嘤(〒︿〒)')
    else:
        await session.send(f"成员{mem['name']}已从{mem['cid']}会删除")


@on_command('add-challenge', aliases=('dmg', ), permission=perm.GROUP, shell_like=True, only_to_me=False)
async def add_challenge(session: CommandSession):
    '''
    这个命令最常用，需要给沙雕群友优化一下语法  ---->  简易版本见 add_challenge_e
    '''
    parser = ArgumentParser(session=session, usage='dmg -r -b damage [--uid] [--alt] [--ext | --last | --timeout]\n对3周目的老五造成114514点伤害：\n【 dmg 114514 -r3 -b5 】\n帮骑士A出了尾刀收了4周目带善人：\n【 dmg 1919810 -r4 -b1 --last --uid [骑士A的QQ] 】')
    parser.add_argument('-r', '--round', type=int)
    parser.add_argument('-b', '--boss', type=int)
    parser.add_argument('damage', type=int, default=-1)
    parser.add_argument('--uid', type=int, default=-1)
    parser.add_argument('--alt', type=int, default=0)
    flag_group = parser.add_mutually_exclusive_group()
    flag_group.add_argument('--ext', action='store_true')
    flag_group.add_argument('--last', action='store_true')
    flag_group.add_argument('--timeout', action='store_true')
    args = parser.parse_args(session.argv)

    flag = BattleMaster.NORM
    if args.last:
        flag = BattleMaster.LAST
    elif args.ext:
        flag = BattleMaster.EXT
    elif args.timeout:
        flag = BattleMaster.TIMEOUT
        args.damage = 0

    challenge = {
        'round': args.round,
        'boss': args.boss,
        'damage': args.damage,
        'uid': args.uid,
        'alt': args.alt,
        'flag': flag
    }
    await process_challenge(session, challenge)


async def process_challenge(session: CommandSession, challenge):
    '''
    处理一条报刀
    需要保证challenge['flag']的正确性
    '''
    group_id = session.ctx['group_id']
    battlemaster = BattleMaster(group_id)
    
    uid = challenge['uid'] if challenge['uid'] > 0 else session.ctx['user_id']
    alt = challenge['alt']
    mem = battlemaster.get_member(uid, alt)
    if not mem:
        await session.finish('本群无法找到该成员，请先使用join-clan命令加入公会后再报刀')
    
    cid = mem['cid']
    clan = battlemaster.get_clan(cid)
    if not clan:
        await session.finish(f'该成员所在分会{cid}已不存在，请重新加入公会')
    
    round_ = challenge['round']
    if round_ <= 0:
        await session.finish('Error: 周目数必须大于0')
    
    boss = challenge['boss']
    if not 1 <= boss <= 5:
        await session.finish('Error: Boss编号只能是1/2/3/4/5')
    
    damage = challenge['damage']
    if damage < 0:
        await session.finish('Error: 未找到正确的伤害数值')
    
    flag = challenge['flag']

    current_round, current_boss, current_hp = battlemaster.get_challenge_progress(
        cid, datetime.now())
    warn_prog = '该伤害上报与当前进度不一致，请注意核对\n' if not (
        round_ == current_round and boss == current_boss) else ''
    warn_last = ''

    # 尾刀伤害校验
    if round_ == current_round and boss == current_boss:
        if damage > current_hp + 50000:        # 忘加尾刀标志、撞刀
            warn_last = '发生过度虐杀，伤害数值已自动修正并标记尾刀，请注意检查是否撞刀\n'
            damage = current_hp
            flag = BattleMaster.LAST
        # 使用整万数报尾刀，伤害不足
        elif flag & BattleMaster.LAST and damage >= current_hp - 50000 and 0 == damage % 10000:
            warn_last = '尾刀伤害已自动校对\n'
            damage = current_hp
        # 报尾刀，但伤害严重不足
        elif flag & BattleMaster.LAST and damage < current_hp - 50000:
            warn_last = '本次尾刀上报后，Boss仍有较多血量，请注意核对并请尚未报刀的成员及时报刀\n'

    if battlemaster.add_challenge(uid, alt, round_, boss, damage, flag, datetime.now()) < 0:
        await session.send('记录添加失败...ごめんなさい！嘤嘤嘤(〒︿〒)')
    else:
        after_round, after_boss, after_hp = battlemaster.get_challenge_progress(
            cid, datetime.now())
        total_hp = battlemaster.get_boss_hp(
            after_round, after_boss, clan['server'])
        score_rate = battlemaster.get_score_rate(
            after_round, after_boss, clan['server'])
        msg1 = f"记录成功！\n{mem['name']}对{round_}周目{battlemaster.int2kanji(boss)}王造成了{damage:,d}点伤害\n"
        msg2 = f"当前{cid}会进度：\n{after_round}周目 {battlemaster.int2kanji(after_boss)}王 HP={after_hp:,d}/{total_hp:,d} x{score_rate:.1f}"
        await session.send(f'{warn_prog}{warn_last}{msg1}{msg2}')

        # 判断是否更换boss，呼叫预约
        # if after_round > current_round or (after_round == current_round and after_boss > current_boss):
        #     await call_reserve(session, after_round, after_boss)


@on_command('add-challenge-e', aliases=('dmge', '刀'), permission=perm.GROUP, only_to_me=False)
async def add_challenge_e(session: CommandSession):
    '''
    简易报刀
    为学不会命令行的沙雕群友准备的简易版报刀命令。目前仅支持给自己的大号报刀
    '''
    USAGE = "使用方法：\n【 dmge 伤害数字 r周目 b老几 [last|ext|timeout] 】\n例：对5周目老4造成了114万点伤害\n【 dmge 114w r5 b4 】"
    challenge = session.state['challenge']
    challenge['uid'] = session.ctx['user_id']
    challenge['alt'] = 0
    flag = challenge['flag']
    f_cnt = (flag == BattleMaster.LAST) + (flag == BattleMaster.EXT) + (flag == BattleMaster.TIMEOUT)
    if f_cnt > 1:
        await session.finish('Error: 出刀记录只能是[尾刀|补时刀|掉刀]中的一种，不可同时使用。\n若「补时刀」收尾请报ext，游戏内一刀不能获得两次补时\n' + USAGE)  # 此时应按ext处理，游戏内一刀不能获得两次补时
    if not challenge['round']:
        await session.finish('Error: 未找到周目数\n' + USAGE)
    if not challenge['boss']:
        await session.finish('Error: 请给出Boss编号\n' + USAGE)
    if flag & BattleMaster.TIMEOUT:
        challenge['damage'] = 0
    if challenge['damage'] < 0:
        await session.finish('Error: 未找到正确的伤害，请输入纯数字\n' + USAGE)

    await process_challenge(session, challenge)


@add_challenge_e.args_parser
async def _(session: CommandSession):
    args = session.current_arg_text.split()
    rex_round = re.compile(r'^-*r(ound)?\d+$', re.I)
    rex_boss = re.compile(r'^-*b(oss)?[1-5]$', re.I)
    rex_dmg = re.compile(r'^\d+w?$', re.I)
    rex_last = re.compile(r'^-*last$', re.I)
    rex_ext = re.compile(r'^-*ext(end)?$', re.I)
    rex_timeout = re.compile(r'^-*timeout$', re.I)
    ret = {
        'round': None,
        'boss': None,
        'damage': -1,
        'flag': BattleMaster.NORM
    }
    for arg in args:
        if rex_round.match(arg):
            ret['round'] = int(arg[1: ])
        elif rex_boss.match(arg):
            ret['boss'] = int(arg[-1])
        elif rex_dmg.match(arg):
            ret['damage'] = 10000 * int(arg[ :-1]) if arg[-1] == 'w' or arg[-1] == 'W' else int(arg)
        elif rex_last.match(arg):
            ret['flag'] = ret['flag'] | BattleMaster.LAST
        elif rex_ext.match(arg):
            ret['flag'] = ret['flag'] | BattleMaster.EXT
        elif rex_timeout.match(arg):
            ret['flag'] = ret['flag'] | BattleMaster.TIMEOUT
            ret['damage'] = 0
    session.state['challenge'] = ret


@on_command('show-progress', permission=perm.GROUP, shell_like=True, only_to_me=False)
async def show_progress(session: CommandSession):
    parser = ArgumentParser(session=session, usage='show-progress [--cid]')
    parser.add_argument('--cid', type=int, default=1)
    args = parser.parse_args(session.argv)

    group_id = session.ctx['group_id']
    battlemaster = BattleMaster(group_id)
    cid = args.cid
    clan = battlemaster.get_clan(cid)
    if not clan:
        await session.finish(f'本群不存在{cid}会')
    round_, boss, remain_hp = battlemaster.get_challenge_progress(cid, datetime.now())
    total_hp = battlemaster.get_boss_hp(round_, boss, clan['server'])
    score_rate = battlemaster.get_score_rate(round_, boss, clan['server'])

    await session.send(f'当前{cid}会进度：\n{round_}周目 老{battlemaster.int2kanji(boss)} HP={remain_hp}/{total_hp} x{score_rate:.1f}')


@on_command('stat', permission=perm.GROUP, shell_like=True, only_to_me=False)
async def stat(session: CommandSession):
    parser = ArgumentParser(session=session, usage='stat [--cid]')
    parser.add_argument('--cid', type=int, default=1)
    args = parser.parse_args(session.argv)

    group_id = session.ctx['group_id']
    cid = args.cid
    battlemaster = BattleMaster(group_id)
    stat = battlemaster.stat_score(cid, datetime.now())
    yyyy, mm, _ = BattleMaster.get_yyyymmdd(datetime.now())

    stat.sort(key=lambda x: x[3], reverse=True)
    msg1 = []
    for uid, alt, name, score in stat:
        # QQ字体非等宽，width(空格*2) == width(数字*1)
        # 数字太多会被腾讯ban，用逗号分隔
        score = f'{score:,d}'
        blank = ' ' * (11-len(score)) * 2
        line = f"{blank}{score}分 {name}\n"

        msg1.append(line)
    await session.send(f'{yyyy}年{mm}月会战{cid}会分数统计：\n' + ''.join(msg1))


@on_command('show-remain', permission=perm.GROUP, shell_like=True, only_to_me=False)
async def show_remain(session: CommandSession):

    parser = ArgumentParser(session=session, usage='show-remain [--cid]')
    parser.add_argument('--cid', type=int, default=1)
    args = parser.parse_args(session.argv)

    group_id = session.ctx['group_id']
    cid = args.cid

    battlemaster = BattleMaster(group_id)

    if not battlemaster.has_clan(cid):
        session.finish(f'本群还没有{cid}会哦！使用list-clan查看本群所有公会')

    stat = battlemaster.list_challenge_remain(cid, datetime.now())

    is_admin = await perm.check_permission(session.bot, session.ctx, perm.GROUP_ADMIN)
    msg1 = []
    for uid, alt, name, rem_n, rem_e in stat:
        if rem_n or rem_e:
            line = ( str(MessageSegment.at(uid)) if is_admin else name ) + \
                   ( f'的小号{alt} ' if alt else '' ) + \
                   ( f' 余{rem_n}刀 补时{rem_e}刀\n' if rem_e else f'余{rem_n}刀\n' )
            msg1.append(line)
        
    if msg1:
        await session.send('今日余刀统计：\n' + ''.join(msg1))
    else:
        await session.send(f'{cid}会所有成员均已出完刀！各位辛苦了！')


@on_command('list-challenge', permission=perm.GROUP, shell_like=True, only_to_me=False)
async def list_challenge(session: CommandSession):
    parser = ArgumentParser(session=session, usage='list-challenge [--cid] [--all]')
    parser.add_argument('--cid', type=int, default=1)
    # parser.add_argument('--uid', type=int, default=-1)
    # parser.add_argument('--alt', type=int, default=0)
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args(session.argv)

    group_id = session.ctx['group_id']
    cid = args.cid

    battlemaster = BattleMaster(group_id)
    clan = battlemaster.get_clan(cid)

    if not clan:
        await session.finish(f'Error: 本群不存在{cid}会')

    now = datetime.now()
    zone = battlemaster.get_timezone_num(clan['server'])
    challen = battlemaster.list_challenge(cid, now) if args.all else battlemaster.list_challenge_of_day(cid, now, zone)

    msg = f'{cid}会出刀记录：\neid|name|round|boss|damage\n'
    challenstr = '{eid:0>3d}|{name}|r{round}|b{boss}|{dmg: >7,d}{flag_str}\n'
    for c in challen:
        mem = battlemaster.get_member(c['uid'], c['alt'])
        c['name'] = mem['name'] if mem else c['uid']
        flag = c['flag']
        c['flag_str'] = '|ext' if flag & BattleMaster.EXT else '|last' if flag & BattleMaster.LAST else '|timeout' if flag & BattleMaster.TIMEOUT else ''
        msg = msg + challenstr.format_map(c)
    await session.send(msg)


@on_command('del-challenge', permission=perm.GROUP, shell_like=True, only_to_me=False)
async def del_challenge(session: CommandSession):
    parser = ArgumentParser(session=session, usage='del-challenge --eid [--cid]')
    parser.add_argument('--eid', type=int)
    parser.add_argument('--cid', type=int, default=1)
    args = parser.parse_args(session.argv)

    eid = args.eid
    group_id = session.ctx['group_id']
    cid = args.cid

    battlemaster = BattleMaster(group_id)
    clan = battlemaster.get_clan(cid)

    if not clan:
        await session.finish(f'Error: 本群不存在{cid}会')

    now = datetime.now()
    challen = battlemaster.get_challenge(eid, cid, now)

    if not challen:
        await session.finish(f'Error: 无法在{cid}会的记录中找到编号为{eid}的出刀记录')

    if challen['uid'] != session.ctx['user_id']:
        if not await perm.check_permission(session.bot, session.ctx, perm.GROUP_ADMIN):
            await session.finish('Error: 只有管理员删除其他人的出刀记录')
    
    if battlemaster.del_challenge(eid, cid, now):
        await session.send('记录删除失败...ごめんなさい！嘤嘤嘤(〒︿〒)')
    else:
        await session.send(f'已成功删除{cid}会的{eid}号出刀记录')


"""
async def call_reserve(session: CommandSession, round_: int, boss_index: int):
    context = session.ctx
    group_id = context['group_id']

    reservation_path = reservations_folder + '\\' + str(group_id)+'.json'
    if os.path.exists(reservation_path):
        reservation = json.load(
            open(reservation_path, 'r'))
        reservation_list = reservation.get(str(boss_index), [])
        reservation[str(boss_index)] = []
        json.dump(reservation, open(reservation_path, 'w'))
        msg = f'公会战已轮到{round_}周目{bossNames[boss_index - 1]}，请尽快出刀，如需下轮请重新预约。'
        for user_id in reservation_list:
            msg += f'\n[CQ:at,qq={user_id}]'
        await session.send(msg)


@on_command('see_reserve', aliases=("查询预约", ), only_to_me=False)
async def _(session: CommandSession):
    context = session.ctx
    if context['message_type'] != 'group':
        return

    group_id = context['group_id']

    reservation_path = reservations_folder + '\\' + str(group_id)+'.json'
    if not os.path.exists(reservation_path):
        await session.send('当前没有Boss预约')
    else:
        msg = "当前各王预约人数："
        reservation = json.load(open(reservation_path, 'r'))
        for index, r_list in reservation.items():
            name = bossNames[int(index) - 1]
            msg += f'\n{name}：{len(r_list)}人'

        await session.send(msg)


async def reserve_function(session: CommandSession, boss_index: int):
    context = session.ctx
    if context['message_type'] != 'group':
        return

    group_id = context['group_id']
    user_id = context['user_id']

    reservation_path = reservations_folder + '\\' + str(group_id)+'.json'
    reservation = default_reservation.copy()
    if os.path.exists(reservation_path):
        reservation = json.load(open(reservation_path, 'r'))
    reservation_list = reservation.get(str(boss_index), [])

    if user_id in reservation_list:
        await session.send(f'[CQ:at,qq={user_id}] 你已预约过{bossNames[boss_index - 1]}，请勿重复预约')
    else:
        reservation_list.append(user_id)
        reservation[str(boss_index)] = reservation_list
        json.dump(reservation, open(reservation_path, 'w'))
        await session.send(f'[CQ:at,qq={user_id}] 你已成功预约{bossNames[boss_index - 1]}，当前Boss预约人数：{len(reservation_list)}')


async def unreserve_function(session: CommandSession, boss_index: int):
    context = session.ctx
    if context['message_type'] != 'group':
        return

    group_id = context['group_id']
    user_id = context['user_id']

    reservation_path = reservations_folder + '\\' + str(group_id)+'.json'
    reservation = default_reservation.copy()
    if os.path.exists(reservation_path):
        reservation = json.load(open(reservation_path, 'r'))
    reservation_list = reservation.get(str(boss_index), [])

    if user_id in reservation_list:
        reservation_list.remove(user_id)
        reservation[str(boss_index)] = reservation_list
        json.dump(reservation, open(reservation_path, 'w'))
        await session.send(f'[CQ:at,qq={user_id}] 已为你取削预约{bossNames[boss_index - 1]}')
    else:
        await session.send(f'[CQ:at,qq={user_id}] 你尚未预约{bossNames[boss_index - 1]}')


@on_command('reserve1', aliases=('预约一王', ), only_to_me=False)
async def _(session: CommandSession):
    await reserve_function(session, 1)


@on_command('reserve2', aliases=('预约二王', ), only_to_me=False)
async def _(session: CommandSession):
    await reserve_function(session, 2)


@on_command('reserve3', aliases=('预约三王', ), only_to_me=False)
async def _(session: CommandSession):
    await reserve_function(session, 3)


@on_command('reserve4', aliases=('预约四王', ), only_to_me=False)
async def _(session: CommandSession):
    await reserve_function(session, 4)


@on_command('reserve5', aliases=('预约五王', ), only_to_me=False)
async def _(session: CommandSession):
    await reserve_function(session, 5)


@on_command('unreserve1', aliases=('取消预约一王', ), only_to_me=False)
async def _(session: CommandSession):
    await unreserve_function(session, 1)


@on_command('unreserve2', aliases=('取消预约二王', ), only_to_me=False)
async def _(session: CommandSession):
    await unreserve_function(session, 2)


@on_command('unreserve3', aliases=('取消预约三王', ), only_to_me=False)
async def _(session: CommandSession):
    await unreserve_function(session, 3)


@on_command('unreserve4', aliases=('取消预约四王', ), only_to_me=False)
async def _(session: CommandSession):
    await unreserve_function(session, 4)


@on_command('unreserve5', aliases=('取消预约五王', ), only_to_me=False)
async def _(session: CommandSession):
    await unreserve_function(session, 5)
"""
