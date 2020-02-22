# 公主连接Re:Dive会战管理插件
# clan == クラン == 戰隊（直译为氏族）（CLANNAD的CLAN（笑））

import re

from nonebot import CommandSession
from nonebot import permission as perm
from hoshino.service import Service, Privilege
from .battlemaster import BattleMaster

sv = Service('clanbattle', manage_priv=Privilege.SUPERUSER, enable_on_default=False)


@sv.on_command('添加公会', only_to_me=False)
async def add_clan(session:CommandSession):
    if not await perm.check_permission(session.bot, session.ctx, perm.GROUP_ADMIN):
        await session.finish('Error: 只有管理员才能添加新公会')

    group_id = session.ctx['group_id']
    bm = BattleMaster(group_id)
    
    name = None
    cid = -1
    server = 'Unknown'

    for arg in reversed(session.current_arg_text.split()):
        if m := re.match(r'n(ame)?(.+)', arg, re.I):
            name = m.group(2)
        elif m := re.match(r'c(id)?(\d+)', arg, re.I):
            cid = int(m.group(2))
        elif m := re.match(r's(erver)?(.+)', arg, re.I):
            server = m.group(2)
    
    if not name:
        ginfo = await session.bot._get_group_info(group_id=group_id)
        name = ginfo['group_name']

    if cid <= 0:
        clans = bm.list_clan()
        for clan in clans:
            cid = clan['cid'] if clan['cid'] > cid else cid
        cid = cid + 1 if cid > 0 else 1

    server = bm.get_server_code(server)
    if server < 0:
        await session.finish('请指定公会所在服务器 例【添加公会 sjp】')

    if bm.add_clan(cid, name, server):
        await session.send('公会添加失败...ごめんなさい！嘤嘤嘤(〒︿〒)')
    else:
        await session.send(f'公会添加成功！{cid}会 {name}')


@sv.on_command('添加成员', aliases=('加入公会', ), only_to_me=False)
async def add_member(session:CommandSession):
    
    cid = 1
    uid = -1
    alt = 0
    name = None
    group_id = session.ctx['group_id']

    for arg in reversed(session.ctx['message']):
        if arg.type == 'text':
            arg = str(arg)
            if m := re.match(r'n(ame)?(.+)', arg, re.I):
                name = m.group(2)
            elif m := re.match(r'c(id)?(\d+)', arg, re.I):
                cid = int(m.group(2))
            elif m := re.match(r'u(id)?(\d+)', arg, re.I):
                uid = int(m.group(2))
            elif m := re.match(r'q(q)?(\d+)', arg, re.I):
                uid = int(m.group(2))
            elif m := re.match(r'a(lt)?(\d+)', arg, re.I):
                alt = int(m.group(2))
        elif arg.type == 'at':
            uid = int(arg.data['qq'])
    
    uid = uid if uid > 0 else session.ctx['user_id']
    try:    # 尝试获取群员信息，用以检查该成员是否在群中
        group_member_info = await session.bot.get_group_member_info(self_id=session.ctx['self_id'], group_id=group_id, user_id=uid)
    except:
        await session.finish(f'Error: 无法获取到指定群员的信息，请检查{uid}是否属于本群\n（注：uid为QQ号，机器人无需九码，如有小号请指定alt参数）')
    if not name:
        name = group_member_info['card']
        if not name.strip():
            session.finish('Error: name参数未指定，且获取群名片为空。请尝试指定name参数（建议使用游戏内昵称）')

    bm = BattleMaster(group_id)
    clan = bm.get_clan(cid)
    if not clan:
        await session.finish(f'Error: 指定的分会{cid}不存在')
    if alt < 0:
        await session.finish('Error: 小号编号不能小于0')
    if uid != session.ctx['user_id']:
        if not await perm.check_permission(session.bot, session.ctx, perm.GROUP_ADMIN):
            await session.finish('Error: 只有管理员才能添加其他人到公会')

    if bm.add_member(uid, alt, name, cid):
        await session.send(f'成员添加失败...ごめんなさい！嘤嘤嘤(〒︿〒)\n请检查帐号{uid}（的小号{alt}）是否已存在于其他公会')
    else:
        msg_alt = f'的{alt}号小号' if alt else ''
        clan_name = clan['name']
        await session.send(f'成员添加成功！欢迎{name}{msg_alt}加入{cid}会 {clan_name}')
