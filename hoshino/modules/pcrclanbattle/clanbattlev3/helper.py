from datetime import timedelta, timezone
from functools import wraps

from hoshino import priv
from hoshino.config import clanbattle as cfg
from hoshino.typing import CQEvent

from .const import *
from .exception import *
from .model import *

ERROR_CLAN_NOTFOUND = '公会未初始化：请群管理发送"建会日/台/B服+公会名"'
ERROR_ZERO_MEMBER = '公会内无成员：请使用"入会"或"批量入会"以添加'
ERROR_MEMBER_NOTFOUND = '未找到成员：请使用"入会+昵称"以添加'
ERROR_PERMISSION_DENIED = "权限不足：需*群管理*以上"


def check_clan(bm, conn) -> Clan:
    clan = bm.clan.get(conn, bm.gid)
    if not clan:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)
    return clan


def check_member(bm, conn, uid: int, tip=None) -> Member:
    mem = bm.member.get(conn, (bm.gid, uid))
    if not mem:
        raise NotFoundError(tip or ERROR_MEMBER_NOTFOUND)
    return mem


def check_admin(ev, tip: str = ""):
    if not priv.check_priv(ev, priv.ADMIN):
        raise PermissionDeniedError(ERROR_PERMISSION_DENIED + tip)


def one_line_str(s: str) -> str:
    return s.replace("\n", " ").strip()


def plain_text(message) -> str:
    return message.extract_plain_text()


def get_at(ev: CQEvent):
    for seg in ev.message:
        if seg.type == "at":
            at = int(seg.data["qq"])
            if at != ev.self_id:
                return at
    return None


def get_at_list(ev: CQEvent):
    ret = []
    for seg in ev.message:
        if seg.type == "at":
            at = int(seg.data["qq"])
            if at != ev.self_id:
                ret.append(at)
    return ret


def handle_clanbattle_error(func):
    @wraps(func)
    async def wrapper(bot, ev, *arg, **kwarg):
        try:
            return await func(bot, ev, *arg, **kwarg)
        except ClanBattleError as e:
            await bot.finish(ev, str(e) or e.__class__.__name__)

    return wrapper


def next_round_boss(round_, boss):
    return (round_, boss + 1) if boss < 5 else (round_ + 1, 1)


def get_stage(round_):
    return 4 if round_ >= 35 else 3 if round_ >= 11 else 2 if round_ >= 4 else 1


def get_boss_hp(round_, boss, server):
    stage = get_stage(round_)
    if server == SERVER.JP:
        hp = cfg.JP.BOSS_HP
    elif server == SERVER.TW:
        hp = cfg.TW.BOSS_HP
    elif server == SERVER.BL:
        hp = cfg.BL.BOSS_HP
    else:
        raise ValueError("Unknown server.")
    return hp[stage - 1][boss - 1]


def yyyymmdd(time, zone_num: int = 8):
    """返回time对应的会战年月日。

    其中，年月为该期会战的年月；日为刷新周期对应的日期。
    会战为每月最后一星期，编程时认为mm月的会战一定在mm月20日至mm+1月10日之间，每日以5:00 UTC+8为界。
    注意：返回的年月日并不一定是自然时间，如2019年9月2日04:00:00我们认为对应2019年8月会战，日期仍为1号，将返回(2019,8,1)
    """
    # 日台服均为当地时间凌晨5点更新，故减5
    time = time.astimezone(timezone(timedelta(hours=zone_num - 5)))
    yyyy = time.year
    mm = time.month
    dd = time.day
    if dd < 20:
        mm = mm - 1
    if mm < 1:
        mm = 12
        yyyy = yyyy - 1
    return (yyyy, mm, dd)


def get_t_alpha(clan):
    return 10 if clan.server == SERVER.BL else 20


def condition_full_refund(dmg, hp, t_alpha):
    return dmg > 90 * hp / (91 + t_alpha)


def dmg_need_for_full_refund(dmg, hp, t_alpha):
    return int(1 + hp - dmg * (t_alpha + 1) / 90)
