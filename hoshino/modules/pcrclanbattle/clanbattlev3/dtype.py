import re

from hoshino import util
from .exception import ParseError
from .const import *

_unit_rate = {"": 1, "k": 1000, "w": 10000, "千": 1000, "万": 10000}
_rex_dint = re.compile(r"^(\d+)([wk千万]?)$", re.I)
_rex1_bcode = re.compile(r"^老?([1-5])王?$")
_rex2_bcode = re.compile(r"^老?([一二三四五])王?$")
_rex_rcode = re.compile(r"^[1-9]\d{0,2}$")


def damage_int(x: str) -> int:
    x = util.normalize_str(x.strip())
    if m := _rex_dint.match(x):
        x = int(m.group(1)) * _unit_rate[m.group(2).lower()]
        if x < 100000000:
            return x
    raise ParseError("伤害值不合法 应为小于一亿的非负整数")


def boss_code(x: str) -> int:
    x = util.normalize_str(x.strip())
    if m := _rex1_bcode.match(x):
        return int(m.group(1))
    elif m := _rex2_bcode.match(x):
        return "零一二三四五".find(m.group(1))
    raise ParseError("Boss编号不合法 应为1-5的整数")


def round_code(x: str) -> int:
    x = util.normalize_str(x.strip())
    if _rex_rcode.match(x):
        return int(x)
    raise ParseError("周目数不合法 应为不大于999的非负整数")


def server_code(x: str) -> int:
    x = util.normalize_str(x.strip())
    if x in ("jp", "日", "日服"):
        return SERVER.JP
    elif x in ("tw", "台", "台服"):
        return SERVER.TW
    elif x in ("cn", "国", "国服", "b", "b服"):
        return SERVER.BL
    raise ParseError("未知服务器地区 请用jp/tw/b")


def server_name(x: int) -> str:
    if x == SERVER.JP:
        return "日服"
    if x == SERVER.TW:
        return "台服"
    if x == SERVER.BL:
        return "B服"
    return "unknown"


def boss_name(x: int) -> str:
    if isinstance(x, int) and 1 <= x <= 5:
        return '零一二三四五'[x] + '王'
    return '?王'


def flag_name(x: int) -> str:
    if x == CHALLENGE.NORM:
        return "完整刀"
    if x == CHALLENGE.LAST:
        return "尾刀"
    if x == CHALLENGE.EXT:
        return "补时刀"
    if x == CHALLENGE.TIMEOUT:
        return "滑刀"
    return "unknown"
