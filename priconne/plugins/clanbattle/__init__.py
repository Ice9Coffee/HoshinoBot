# 公主连接Re:Dive会战管理插件
# clan == クラン == 戰隊（直译为氏族）（CLANNAD的CLAN（笑））

from datetime import datetime
import re

from nonebot import on_command, CommandSession, MessageSegment
from nonebot.permission import *
from nonebot.argparse import ArgumentParser
from .battlemaster import BattleMaster


@on_command('add-clan', permission=SUPERUSER|GROUP_OWNER, shell_like=True, only_to_me=False)
async def add_clan(session: CommandSession):
    parser = ArgumentParser(session=session, usage='add-clan --name [--cid]')
    parser.add_argument('--name', default=None, required=False)
    parser.add_argument('--cid', type=int, default=-1)
    args = parser.parse_args(session.argv)
    group_id = session.ctx['group_id']
    battlemaster = BattleMaster(group_id)

    name = args.name
    if not name:
        ginfo = await session.bot._get_group_info(group_id=group_id)
        name = ginfo['group_name']

    cid = args.cid
    if cid <= 0:
        clans = battlemaster.list_clan()
        for clan in clans:
            cid = clan['cid'] if clan['cid'] > cid else cid
        cid = cid + 1 if cid > 0 else 1

    if battlemaster.add_clan(cid, name):
        await session.send('公会添加失败...ごめんなさい！嘤嘤嘤(〒︿〒)')
    else:
        await session.send(f'公会添加成功！{cid}会 {name}')


@on_command('list-clan', permission=GROUP_MEMBER, only_to_me=False)
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


@on_command('add-member', aliases=('join-clan', ), permission=GROUP_MEMBER, shell_like=True, only_to_me=False)
async def add_member(session: CommandSession):
    parser = ArgumentParser(session=session, usage='add-member/join-clan [--cid] [--uid] [--alt] [--name]\n加入1会: join-clan --name [这里写游戏内的ID（不填将自动获取群名片）]\n将骑士A的小号2加入3会：add-member --uid [骑士A的QQ号] --alt 2 --cid 3 --name [骑士A的游戏ID]')
    parser.add_argument('--cid', type=int, default=1)
    parser.add_argument('--uid', type=int, default=-1)
    parser.add_argument('--alt', type=int, default=0)
    parser.add_argument('--name', default=None)
    args = parser.parse_args(session.argv)

    group_id = session.ctx['group_id']
    cid = args.cid
    uid = args.uid if args.uid > 0 else session.ctx['user_id']
    group_member_info = await session.bot.get_group_member_info(group_id=group_id, user_id=uid)
    alt = args.alt
    name = args.name if args.name else group_member_info['card']

    battlemaster = BattleMaster(group_id)
    clan = battlemaster.get_clan(cid)
    if not clan:
        await session.finish(f'Error: 指定的分会{cid}不存在')
    if alt < 0:
        await session.finish('Error: 小号编号不能小于0')
    if uid != session.ctx['user_id']:
        if not await check_permission(session.bot, session.ctx, SUPERUSER|GROUP_ADMIN):
            await session.finish('Error: 只有管理员才能添加其他人到公会')
    

    if battlemaster.add_member(uid, alt, name, cid):
        await session.send('成员添加失败...ごめんなさい！嘤嘤嘤(〒︿〒)\n请检查该帐号（的该小号）是否已存在于其他公会')
    else:
        msg_alt = f'的{alt}号小号' if alt else ''
        clan_name = clan['name']
        await session.send(f'成员添加成功！欢迎{name}{msg_alt}加入{cid}会 {clan_name}')


@on_command('list-member', permission=GROUP_MEMBER, shell_like=True, only_to_me=False)
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
        msg = f'{cid}会成员一览：  {len(cmems)}/30\n'
        memstr = '{uid: <11d} {name}\n'
        memstr_alt = '{uid: <11d} {name} 小号{alt}\n'
        for m in cmems:
            msg = msg + (memstr.format_map(m) if not m['alt'] else memstr_alt.format_map(m))
        await session.send(msg)
    else:
        await session.send(f'{cid}会目前还没有成员')


@on_command('add-challenge', aliases=('dmg', ), permission=GROUP_MEMBER, shell_like=True, only_to_me=False)
async def add_challenge(session: CommandSession):
    '''
    TODO: 这个命令最常用，需要给沙雕群友优化一下语法    // 简易版本见 add_challenge_e
    '''
    parser = ArgumentParser(session=session, usage='dmg -r -b damage [--uid] [--alt] [--ext | --last | --timeout]\n对3周目的老五造成114514点伤害：dmg 114514 -r 3 -b 5\n帮骑士A出了尾刀收了4周目带善人：dmg 1919810 -r 4 -b 1 --last --uid [骑士A的QQ]')
    parser.add_argument('-r', '--round', type=int)
    parser.add_argument('-b', '--boss', type=int)
    parser.add_argument('damage', type=int)
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
    if not battlemaster.has_clan(cid):
        await session.finish('该成员所在分会已被删除，请重新加入公会')
    
    round_ = challenge['round']
    if round_ <= 0:
        await session.finish('Error: 周目数必须大于0')
    
    boss = challenge['boss']
    if not 1 <= boss <= 5:
        await session.finish('Error: Boss编号只能是1/2/3/4/5')
    
    damage = challenge['damage']
    if damage < 0:
        await session.finish('Error: 伤害值不能为负')
    
    flag = challenge['flag']

    prog = battlemaster.get_challenge_progress(cid, datetime.now())
    msg0 = '该伤害上报与当前进度不一致，请注意核对\n' if not (round_ == prog[0] and boss == prog[1]) else ''
    msg00 = ''

    if damage > prog[2] + 50000:
        msg00 = '发生过度虐杀，伤害数值已自动修正并标记尾刀，请注意检查是否撞刀\n'
        damage = prog[2]
        flag = BattleMaster.LAST
    elif flag & BattleMaster.LAST and damage >= prog[2] - 50000 and 0 == damage % 10000:
        msg00 = '尾刀伤害已自动校对\n'
        damage = prog[2]
    elif flag & BattleMaster.LAST and damage < prog[2] - 50000:
        msg00 = '本次尾刀上报后，Boss仍有较多血量，请注意核对并请尚未报刀的成员及时报刀\n'

    if battlemaster.add_challenge(uid, alt, round_, boss, damage, flag, datetime.now()):
        await session.send('记录添加失败...ごめんなさい！嘤嘤嘤(〒︿〒)')
    else:
        prog = battlemaster.get_challenge_progress(cid, datetime.now())
        total_hp = battlemaster.get_boss_hp(prog[1])
        score_rate = battlemaster.get_score_rate(prog[0], prog[1])
        msg1 = f"记录成功！\n{mem['name']}对{round_}周目老{battlemaster.int2kanji(boss)}造成了{damage}点伤害\n"
        msg2 = f"当前{cid}会进度：\n{prog[0]}周目 老{battlemaster.int2kanji(prog[1])} HP={prog[2]}/{total_hp} x{score_rate:.1f}"
        await session.send(msg0 + msg00 + msg1 + msg2)


@on_command('add-challenge-e', aliases=('dmge', '刀'), permission=GROUP_MEMBER, only_to_me=False)
async def add_challenge_e(session: CommandSession):
    '''
    简易报刀
    为学不会命令行的沙雕群友准备的简易版报刀命令。目前仅支持给自己的大号报刀
    '''
    USAGE = "使用方法：\ndmge 伤害数字 r周目 b老几 [last|ext|timeout]\n例：对5周目老4造成了1919810点伤害\ndmge 1919810 r5 b4 "
    challenge = session.state['challenge']
    challenge['uid'] = session.ctx['user_id']
    challenge['alt'] = 0
    flag = challenge['flag']
    f_cnt = (flag == BattleMaster.LAST) + (flag == BattleMaster.EXT) + (flag == BattleMaster.TIMEOUT)
    if f_cnt > 1:
        await session.finish('Error: 出刀记录只能是[尾刀|补时刀|掉刀]中的一种，不可同时使用。\n补时刀收尾请报ext，游戏内一刀不能获得两次补时\n' + USAGE)  # TODO: 似乎可以用补时刀收尾？ // 此时应按ext处理，游戏内一刀不能获得两次补时
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
    rex_round = re.compile(r'r\d+', re.I)
    rex_boss = re.compile(r'b[1-5]', re.I)
    rex_dmg = re.compile(r'\d+w?', re.I)
    rex_last = re.compile(r'last', re.I)
    rex_ext = re.compile(r'ext(end)?', re.I)
    rex_timeout = re.compile(r'timeout', re.I)
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
            ret['boss'] = int(arg[1])
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


@on_command('show-progress', permission=GROUP_MEMBER, shell_like=True, only_to_me=False)
async def show_progress(session: CommandSession):
    parser = ArgumentParser(session=session, usage='show-progress [--cid]')
    parser.add_argument('--cid', type=int, default=1)
    args = parser.parse_args(session.argv)

    group_id = session.ctx['group_id']
    battlemaster = BattleMaster(group_id)
    cid = args.cid
    if not battlemaster.has_clan(cid):
        await session.finish(f'本群不存在{cid}会')
    round_, boss, remain_hp = battlemaster.get_challenge_progress(cid, datetime.now())
    total_hp = battlemaster.get_boss_hp(boss)
    score_rate = battlemaster.get_score_rate(round_, boss)

    await session.send(f'当前{cid}会进度：\n{round_}周目 老{battlemaster.int2kanji(boss)} HP={remain_hp}/{total_hp} x{score_rate:.1f}')


@on_command('stat', permission=GROUP_MEMBER, shell_like=True, only_to_me=False)
async def stat(session: CommandSession):

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
        digi = get_digi(score)      # QQ字体非等宽，width(空格*2) == width(数字*1)
        line = f"{' '*(10-digi)*2}{score}分 {name}\n"
        msg1.append(line)
    await session.send(f'{yyyy}年{mm}月会战{cid}会分数统计：\n' + ''.join(msg1))


@on_command('show-remain', permission=GROUP_MEMBER, shell_like=True, only_to_me=False)
async def show_remain(session: CommandSession):
    parser = ArgumentParser(session=session, usage='show-remain [--cid]')
    parser.add_argument('--cid', type=int, default=1)
    args = parser.parse_args(session.argv)
    
    group_id = session.ctx['group_id']
    cid = args.cid
    battlemaster = BattleMaster(group_id)
    stat = battlemaster.list_challenge_remain(cid, datetime.now())

    msg1 = []
    for uid, alt, name, rem_n, rem_e in stat:
        if rem_n or rem_e:
            line = ( str(MessageSegment.at(uid)) if check_permission(session.bot, session.ctx, GROUP_ADMIN) else name ) + \
                   ( f'的小号{alt} ' if alt else '' ) + \
                   ( f' 余{rem_n}刀 补时{rem_e}刀\n' if rem_e else f'余{rem_n}刀\n' )
            msg1.append(line)
    if msg1:
        await session.send('今日余刀统计：\n' + ''.join(msg1))
    else:
        await session.send('所有成员均已出完刀！各位辛苦了！')