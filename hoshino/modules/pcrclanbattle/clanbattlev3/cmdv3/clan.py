from datetime import datetime

from hoshino.typing import CQEvent, MessageSegment

from ..battlemaster import BattleMaster as Master
from ..const import *
from ..dtype import *
from ..exception import *
from ..helper import *
from ..model import *
from . import sv


@handle_clanbattle_error
async def add_clan(bot, ev: CQEvent, server):
    check_admin(ev, "才能建会")
    gid = ev.group_id
    name = one_line_str(plain_text(ev.message))
    if not name:
        ginfo = await bot.get_group_info(self_id=ev.self_id, group_id=ev.group_id)
        name = ginfo["group_name"]
    if not name:
        name = "Unknown"

    clan = Clan(gid, name, server)
    bm = Master(gid)
    with bm.connect_clan_db() as conn:
        bm.clan.add(conn, clan)
    msg = f"公会信息已登记！\n公会名：{name}\n服务器：{server_name(server)}"
    await bot.send(ev, msg)


@sv.on_prefix(("建会日服", "建立日服公会"))
async def _(bot, ev: CQEvent):
    await add_clan(bot, ev, SERVER.JP)


@sv.on_prefix(("建会台服", "建立台服公会"))
async def _(bot, ev):
    await add_clan(bot, ev, SERVER.TW)


@sv.on_prefix(("建会B服", "建会b服", "建会陆服", "建立B服公会", "建立b服公会", "建立陆服公会"))
async def _(bot, ev):
    await add_clan(bot, ev, SERVER.BL)


@sv.on_prefix(("入会", "加入公会"))
@handle_clanbattle_error
async def add_member(bot, ev: CQEvent):
    gid = ev.group_id
    bm = Master(gid)
    uid = get_at(ev) or ev.user_id
    if uid != ev.user_id:
        check_admin(ev, "才能邀请其他人")
        minfo = await bot.get_group_member_info(
            self_id=ev.self_id, group_id=gid, user_id=uid
        )
    else:
        minfo = ev.sender
    name = (
        one_line_str(plain_text(ev.message))
        or one_line_str(minfo["card"])
        or one_line_str(minfo["nickname"])
        or "祐樹"
    )
    with bm.connect_clan_db() as conn:
        clan = check_clan(bm, conn)
        member = Member(uid, gid, name)
        bm.member.add(conn, member)
    msg = f"欢迎加入{clan.name}！\n骑士名：{name}"
    await bot.send(ev, msg)


@sv.on_prefix("退会")
@handle_clanbattle_error
async def del_member(bot, ev: CQEvent):
    gid = ev.group_id
    bm = Master(gid)
    arg = plain_text(ev.message).strip()
    if arg:
        try:
            uid = int(arg)
        except ValueError:
            raise ParseError('命令解析失败！发送"退会+QQ号"移出其他成员')
    else:
        uid = get_at(ev) or ev.user_id

    with bm.connect_clan_db() as conn:
        mem = check_member(bm, conn, uid, "公会内无此成员")
        if uid != ev.user_id:
            check_admin(ev, "才能移出其他成员")
        bm.member.remove(conn, (bm.gid, uid))
    msg = f"已将{mem.name}移出本会"
    await bot.send(ev, msg)


@sv.on_fullmatch("查看成员")
async def list_member(bot, ev):
    pass
    # TODO


@sv.on_fullmatch(("一键入会", "批量入会", "加入全部成员"))
async def add_member_all(bot, ev):
    pass
    # TODO

@sv.on_fullmatch(("清空成员", "删除全部成员"))
async def clear_member(bot, ev):
    pass
    # TODO
