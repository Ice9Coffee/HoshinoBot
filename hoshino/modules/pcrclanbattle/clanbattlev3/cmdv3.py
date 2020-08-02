from datetime import datetime
from hoshino import Service, priv
from hoshino.typing import *

from .battlemaster import BattleMaster as Master
from .const import *
from .model import *
from .dtype import *

sv = Service('clanbattlev3', bundle='pcr会战', help_='Hoshino会战管理v3（还没写完酷Q就没了 悲）')

ERROR_CLAN_NOTFOUND = f'公会未初始化：请群管理发送"建会日/台/B服+公会名"'
ERROR_ZERO_MEMBER = f'公会内无成员：请使用"入会"或"批量入会"以添加'
ERROR_MEMBER_NOTFOUND = f'未找到成员：请使用"入会+昵称"以添加'
ERROR_PERMISSION_DENIED = '权限不足：需*群管理*以上权限'

# =============== helper functions ================= #

async def _check_clan(bot, ev, bm: Master) -> Clan:
    clan = bm.get_clan()
    if not clan:
        await bot.finish(ev, ERROR_CLAN_NOTFOUND)
    return clan

async def _check_member(bot, ev, bm: Master, uid:int, tip=None) -> Member:
    mem = bm.get_member(uid)
    if not mem:
        await bot.finish(ev, tip or ERROR_MEMBER_NOTFOUND)
    return mem

async def _check_admin(bot, ev, tip:str=''):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, ERROR_PERMISSION_DENIED + tip)

def _get_at(ev: CQEvent):
    for seg in ev.message:
        if seg.type == 'at':
            at = int(seg.data['qq'])
            if at != ev.self_id:
                return at
    return None
                
                
# ================================================== #

async def add_clan(bot, ev: CQEvent, server):
    await _check_admin(bot, ev, '才能建会')
    gid = ev.group_id
    name = one_line_str(ev.message.extract_plain_text())
    if not name:
        ginfo = await bot.get_group_info(self_id=ev.self_id, group_id=ev.group_id)
        name = ginfo['group_name']
    if not name:
        name = 'Unknown'
    clan = Clan(gid, name, server)
    bm = Master(gid, datetime.now())
    bm.add_clan(clan)
    msg = f"公会信息已登记！\n公会名：{name}\n服务器：{server_name(server)}"
    await bot.send(ev, msg)


@sv.on_prefix(('建会日服', '建立日服公会'))
async def _(bot, ev: CQEvent):
    await add_clan(bot, ev, SERVER.JP)

@sv.on_prefix(('建会台服', '建立台服公会'))
async def _(bot, ev):
    await add_clan(bot, ev, SERVER.TW)

@sv.on_prefix(('建会B服', '建会b服', '建会陆服', '建立B服公会', '建立b服公会', '建立陆服公会'))
async def _(bot, ev):
    await add_clan(bot, ev, SERVER.CN)


@sv.on_prefix(('入会', '加入公会'))
async def add_member(bot, ev: CQEvent):
    gid = ev.group_id
    bm = Master(gid, datetime.now())
    clan = await _check_clan(bot, ev, bm)
    uid = _get_at(ev) or ev.user_id
    if uid != ev.user_id:
        await _check_admin(bot, ev)
        minfo = await bot.get_group_member_info(self_id=ev.self_id, group_id=gid, user_id=uid)
    else:
        minfo = ev.sender
    name = one_line_str(ev.message.extract_plain_text()) or \
           one_line_str(minfo['card']) or one_line_str(minfo['nickname']) or '祐樹'
    member = Member(uid, gid, name)
    bm.add_member(member)
    msg = f"欢迎{MessageSegment.at(uid)}加入{clan.name}！\n骑士名：{name}"
    await bot.send(ev, msg)


@sv.on_prefix('退会')
async def del_member(bot, ev: CQEvent):
    gid = ev.group_id
    bm = Master(gid, datetime.now())
    arg = ev.message.extract_plain_text().strip()
    if arg:
        try:
            uid = int(arg)
        except ValueError:
            await bot.finish(ev, '参数错误！\n发送"退会"退出自己\n发送"退会+QQ号"退出其他成员')
    else:
        uid = _get_at(ev) or ev.user_id
    mem = await _check_member(bot, ev, bm, uid, '公会内无此成员')
    if uid != ev.user_id:
        await _check_admin(bot, ev, '才能移出其他成员')
    bm.del_member(uid)
    msg = f"已将{mem.name}移出本会"
    await bot.send(ev, msg)


@sv.on_fullmatch('查看成员')
async def list_member(bot, ev):
    pass

@sv.on_fullmatch(('一键入会', '批量入会', '加入全部成员'))
async def add_member_all(bot, ev):
    pass

@sv.on_fullmatch(('清空成员', '删除全部成员'))
async def clear_member(bot, ev):
    pass


# ================================================== #


@sv.on_prefix(('报刀', '出刀'))
async def add_challenge(bot, ev):
    pass


@sv.on_prefix(('尾刀', '收尾'))
async def _(bot, ev):
    await bot.send(ev, '避免误触，击杀Boss请发送"确认尾刀"')

@sv.on_prefix(('确认尾刀', '确认秒杀', '确认收尾'))
async def add_challenge_last(bot, ev):
    pass


@sv.on_prefix(('掉刀', '滑刀'))
async def add_challenge_timeout(bot, ev):
    pass



@sv.on_prefix(('删刀', '撤销'))
async def del_challenge(bot, ev):
    pass


@sv.on_fullmatch(('状态', '进度'))
async def show_progress(bot, ev):
    pass

    # TODO
    # 周目 Boss 分数倍率 血量
    # 出刀队列（含白嫖刀计算)
    # 预约队列
    # 挂树队列



@sv.on_prefix('预约')
async def add_subr(bot, ev):
    pass


@sv.on_prefix(('取消', '取消预约'))
async def del_subr(bot, ev):
    pass


@sv.on_prefix(('查', '查预约'))
async def list_subr(bot, ev):
    pass


@sv.on_prefix(('清预约', '清空预约', '清理预约'))
async def clear_subr(bot, ev):
    pass


@sv.on_prefix('预约上限')
async def set_subr_limit(bot, ev):
    pass

@sv.on_fullmatch(('挂树', '上树'))
async def add_sos(bot, ev):
    pass


@sv.on_fullmatch('查树')
async def list_sos(bot, ev):
    pass


@sv.on_fullmatch(('我进了', '那我进了', '申请出刀', '锁定'))
async def join_battle_queue(bot, ev):
    pass

@sv.on_fullmatch(('我出了', '我不进了', '解锁'))
async def quit_battle_queue(bot, ev):
    pass


async def log_pause(bot, ev, dmg:int=0, time_left:int=0):
    pass

@sv.on_prefix('暂停')
async def _(bot, ev):
    await log_pause(bot, ev)

@sv.on_rex(r'^(?P<t>\d+)s\s*(?P<dmg>\d+)w$')
@sv.on_rex(r'^(?P<dmg>\d+)w\s*(?P<t>\d+)s$')
async def _(bot, ev):
    await log_pause(bot, ev)


@sv.on_fullmatch('sl')
async def log_sl(bot, ev):
    pass


@sv.on_fullmatch('统计')
async def stat(bot, ev):
    pass

@sv.on_fullmatch('查刀')
async def list_remain(bot, ev):
    pass

@sv.on_fullmatch('催刀')
async def urge_remain(bot, ev):
    pass


