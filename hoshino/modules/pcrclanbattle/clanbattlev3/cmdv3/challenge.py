from datetime import datetime

from hoshino.typing import CQEvent

from .. import renderer
from ..argparser import ArgParser
from ..battlemaster import BattleMaster as Master
from ..const import *
from ..dtype import *
from ..exception import *
from ..helper import *
from ..model import *
from . import sv


@handle_clanbattle_error
async def handle_challenge(bot, ev: CQEvent, ch: Challenge):
    bm = Master(ev.group_id)
    with bm.connect_clan_db() as conn:
        clan = check_clan(bm, conn)
        mem = check_member(bm, conn, ch.uid)
    with bm.connect_battle_db() as conn:
        prog = bm.progress.get(conn)
        ch.round = prog.round
        ch.boss = prog.boss
        if ch.flag == CHALLENGE.LAST:
            ch.dmg = prog.hp
            prog.round, prog.boss = next_round_boss(prog.round, prog.boss)
            prog.hp = get_boss_hp(prog.round, prog.boss, clan.server)
            bm.pause.clear(conn)
        else:
            prog.hp -= ch.dmg
            bm.pause.remove(conn, ch.uid)
        if prog.hp <= 0:
            await bot.finish(ev, '伤害超出当前血量 击杀请用"确认尾刀"')
        if bm.challenge.get_latest_flag(conn, ch.uid) == CHALLENGE.LAST:
            ch.flag = CHALLENGE.EXT
        bm.challenge.add(conn, ch)
        bm.progress.add(conn, prog)
    msg = [
        f"记录编号{ch.eid}",
        f"┣{mem.name} {flag_name(ch.flag)}",
        f"┗造成 {ch.dmg:,d} 点伤害",
        renderer.progress(prog, clan)
    ]
    await bot.send(ev, '\n'.join(msg))


@sv.on_prefix(("报刀", "出刀"))
@handle_clanbattle_error
async def add_challenge(bot, ev: CQEvent):
    dmg = damage_int(plain_text(ev.message))
    if dmg < 1000:
        await bot.finish(ev, "干嘛呢？弟弟")

    ch = Challenge(
        eid=0,
        uid=get_at(ev) or ev.user_id,
        time=datetime.now(),
        round=0,
        boss=0,
        dmg=dmg,
        flag=CHALLENGE.NORM,
    )
    await handle_challenge(bot, ev, ch)


@sv.on_fullmatch(("尾刀", "收尾"))
async def _(bot, ev):
    await bot.send(ev, '避免误触，击杀Boss请发送"确认尾刀"')


@sv.on_prefix(("确认尾刀", "确认秒杀", "确认收尾"))
async def add_challenge_last(bot, ev):
    ch = Challenge(
        eid=0,
        uid=get_at(ev) or ev.user_id,
        time=datetime.now(),
        round=0,
        boss=0,
        dmg=0,
        flag=CHALLENGE.LAST,
    )
    await handle_challenge(bot, ev, ch)


@sv.on_prefix(("掉刀", "滑刀"))
async def add_challenge_timeout(bot, ev):
    ch = Challenge(
        eid=0,
        uid=get_at(ev) or ev.user_id,
        time=datetime.now(),
        round=0,
        boss=0,
        dmg=0,
        flag=CHALLENGE.TIMEOUT,
    )
    await handle_challenge(bot, ev, ch)


@sv.on_prefix(("删刀", "撤销"))
@handle_clanbattle_error
async def del_challenge(bot, ev):
    pass
    # TODO


parser = ArgParser()
parser.add_arg("", "伤害值", damage_int)
parser.add_arg("R", "R周目数", round_code)
parser.add_arg("B", "B王编号", boss_code)
parser.add_arg("@", "@代报QQ", int)


def parse_challenge(ev: CQEvent) -> Challenge:
    args = plain_text(ev.message).split()
    r = parser.parse(args)
    return Challenge(
        eid=0,
        uid=r["@"] or get_at(ev) or ev.user_id,
        time=datetime.now(),
        round=r["R"],
        boss=r["B"],
        dmg=r[""],
        flag=0,
    )


@sv.on_prefix("补报")
@handle_clanbattle_error
async def add_old_challenge(bot, ev):
    pass
    # TODO
