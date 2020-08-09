from hoshino import get_bot, priv
from hoshino.config import clanbattle as cfg
from hoshino.typing import CQEvent, List

from .const import *
from .exception import *
from .model import *
from .dtype import *
from .helper import *


def render_list(lines):
    n = len(lines)
    if n == 0:
        return ""
    if n == 1:
        return "┗" + lines[0]
    return "┣" + "\n┣".join(lines[:-1]) + "\n┗" + lines[-1]


def pause_list(names, pauses: List[PauseRecord], clan, prog, prompt):
    n = len(pauses)
    if not n:
        return prompt
    lines = []
    for i in range(n):
        p = pauses[i]
        line = names[i]
        if p.dmg:
            line += f"：{(p.dmg // 10000):d}w"
            if p.second_left:
                line += f" {p.second_left}s"
        lines.append(line)
    msg = [prompt, render_list(lines)]

    t_alpha = get_t_alpha(clan)
    dmg = pauses[0].dmg
    if condition_full_refund(dmg, prog.hp, t_alpha):
        dmg_need = dmg_need_for_full_refund(dmg, prog.hp, t_alpha)
        msg.append(f"最高刀获满补时需垫{dmg_need:,d}点伤害" if dmg_need > 0 else "最高刀已可获满补时")

    return "\n".join(msg)


def progress(prog, clan):
    return (
        f"当前{prog.round}周目 {boss_name(prog.boss)}\n"
        f"┗{prog.hp:,d}/{get_boss_hp(prog.round, prog.boss, clan.server):,d}"
    )
