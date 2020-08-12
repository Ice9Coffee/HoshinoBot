from hoshino.typing import *

from .. import renderer
from ..battlemaster import BattleMaster as Master
from ..dtype import *
from ..helper import *
from ..model import *
from . import sv


@sv.on_fullmatch(("我进了", "那我进了", "申请出刀", "锁定"))
@handle_clanbattle_error
async def join_battle_queue(bot, ev: CQEvent):
    bm = Master(ev.group_id)
    with bm.connect_clan_db() as conn:
        check_clan(bm, conn)
        check_member(bm, conn, ev.user_id)
    with bm.connect_battle_db() as conn:
        bm.pause.add(conn, PauseRecord(ev.user_id, 0, 0))
        count = bm.pause.count(conn)
    msg = ["已登记进本", f"┗当前战斗人数：{count}"]
    await bot.send(ev, "\n".join(msg))


@sv.on_fullmatch(("我出了", "我不进了", "解锁"))
@handle_clanbattle_error
async def quit_battle_queue(bot, ev: CQEvent):
    bm = Master(ev.group_id)
    with bm.connect_clan_db() as conn:
        check_clan(bm, conn)
        check_member(bm, conn, ev.user_id)
    with bm.connect_battle_db() as conn:
        bm.pause.remove(conn, ev.user_id)
        count = bm.pause.count(conn)
    msg = ["已登记出本", f"┗当前战斗人数：{count}"]
    await bot.send(ev, "\n".join(msg))


@sv.on_rex(r"^(?P<t>\d{0,3}?)(s|\s*)(?P<dmg>\d+)w$")
@sv.on_rex(r"^(?P<dmg>\d+)w\s*(?P<t>\d{0,3})s?$")
@handle_clanbattle_error
async def log_pause(bot, ev: CQEvent):
    bm = Master(ev.group_id)
    dmg = int(ev.match.group("dmg")) * 10000
    time = ev.match.group("t")
    time = int(time) if time else 0
    if time >= 100:
        time -= 40  # convert 1min to 60s
    pause = PauseRecord(ev.user_id, dmg, time)
    with bm.connect_clan_db() as conn1, bm.connect_battle_db() as conn2:
        clan = check_clan(bm, conn1)
        check_member(bm, conn1, ev.user_id)
        bm.pause.add(conn2, pause)
        pauses = bm.pause.list(conn2)
        prog = bm.progress.get(conn2)
        names = bm.uid2name(conn1, [p.uid for p in pauses])

    msg = renderer.pause_list(names, pauses, clan, prog, "已登记出本前暂停")
    await bot.send(ev, msg)
