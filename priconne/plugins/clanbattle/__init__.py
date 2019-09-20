# 公主连接Re:Dive会战管理插件
# clan == クラン == 戰隊（直译为氏族）（CLANNAD的CLAN（笑））

from datetime import datetime

from nonebot import on_command, CommandSession
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
        await session.pause(f'Error: 指定的分会{cid}不存在')
    if alt < 0:
        await session.pause('Error: 小号编号不能小于0')
    if uid != session.ctx['user_id']:
        if not await check_permission(session.bot, session.ctx, SUPERUSER|GROUP_ADMIN):
            await session.pause('Error: 只有管理员才能添加其他人到公会')
    

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
        await session.pause('Error: 指定的分会不存在')
    mems = battlemaster.list_member()
    cmems = []
    for m in mems:
        if m['cid'] == cid:
            cmems.append(m)
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

    group_id = session.ctx['group_id']
    battlemaster = BattleMaster(group_id)
    
    uid = args.uid if args.uid > 0 else session.ctx['user_id']
    alt = args.alt
    mem = battlemaster.get_member(uid, alt)
    if not mem:
        await session.pause('本群无法找到该成员，请先使用join-clan命令加入公会后再报刀')
    
    cid = mem['cid']
    if not battlemaster.has_clan(cid):
        await session.pause('该成员所在分会已被删除，请重新加入公会')
    
    round_ = args.round
    if round_ <= 0:
        await session.pause('Error: 周目数必须大于0')
    
    boss = args.boss
    if not 1 <= boss <= 5:
        await session.pause('Error: Boss编号只能是1/2/3/4/5')
    
    damage = args.damage
    if damage < 0:
        await session.pause('Error: 伤害值不能为负')
    
    flag = battlemaster.NORM
    if args.last:
        flag = battlemaster.LAST
    elif args.ext:
        flag = battlemaster.EXT
    elif args.timeout:
        flag = battlemaster.TIMEOUT
        damage = 0

    prog = battlemaster.get_challenge_progress(cid, datetime.now())
    msg0 = '该伤害上报与当前进度不一致，请注意核对\n' if not (round_ == prog[0] and boss == prog[1]) else ''


    if battlemaster.add_challenge(uid, alt, round_, boss, damage, flag, datetime.now()):
        await session.send('记录添加失败...ごめんなさい！嘤嘤嘤(〒︿〒)')
    else:
        prog = battlemaster.get_challenge_progress(cid, datetime.now())
        total_hp = battlemaster.get_boss_hp(prog[1])
        score_rate = battlemaster.get_score_rate(prog[0], prog[1])
        msg1 = f"记录成功！\n{mem['name']}对{round_}周目老{battlemaster.int2kanji(boss)}造成了{damage}点伤害\n"
        msg2 = f"当前{cid}会进度：\n{prog[0]}周目 老{battlemaster.int2kanji(prog[1])} HP={prog[2]}/{total_hp} x{score_rate:.1f}"
        await session.send(msg0 + msg1 + msg2)


@on_command('show-progress', permission=GROUP_MEMBER, shell_like=True, only_to_me=False)
async def show_progress(session: CommandSession):
    parser = ArgumentParser(session=session, usage='show-progress [--cid]')
    parser.add_argument('--cid', type=int, default=1)
    args = parser.parse_args(session.argv)

    group_id = session.ctx['group_id']
    battlemaster = BattleMaster(group_id)
    cid = args.cid
    if not battlemaster.has_clan(cid):
        await session.pause(f'本群不存在{cid}会')
    round_, boss, remain_hp = battlemaster.get_challenge_progress(cid, datetime.now())
    total_hp = battlemaster.get_boss_hp(boss)
    score_rate = battlemaster.get_score_rate(round_, boss)

    await session.send(f'当前{cid}会进度：\n{round_}周目 老{battlemaster.int2kanji(boss)} HP={remain_hp}/{total_hp} x{score_rate:.1f}')
