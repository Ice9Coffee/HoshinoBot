from hoshino.typing import *

from .. import renderer
from ..battlemaster import BattleMaster as Master
from ..const import *
from ..dtype import *
from ..helper import *
from ..model import *
from . import sv


@sv.on_fullmatch(("状态", "进度", "查当前"))
@handle_clanbattle_error
async def show_progress(bot, ev: CQEvent):
    bm = Master(ev.group_id)
    with bm.connect_clan_db() as conn1, bm.connect_battle_db() as conn2:
        clan = check_clan(bm, conn1)
        prog = bm.progress.get(conn2)
        pauses = bm.pause.list(conn2)
        names = bm.uid2name(conn1, [p.uid for p in pauses])

    msg = [
        renderer.progress(prog, clan),
        renderer.pause_list(names, pauses, clan, prog, f'战斗中：{len(pauses)}人'),
        # TODO: 预约队列
        # TODO: 挂树队列
    ]
    await bot.send(ev, '\n'.join(msg))

# TODO: 调整进度
