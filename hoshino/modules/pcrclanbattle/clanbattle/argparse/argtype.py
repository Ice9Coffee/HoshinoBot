import re

from hoshino import util
from ..exception import ParseError
from ..battlemaster import BattleMaster

_unit_rate = {'': 1, 'k': 1000, 'w': 10000, '千': 1000, '万': 10000}
_rex_dint = re.compile(r'^(\d+)([wk千万]?)$', re.I)
_rex1_bcode = re.compile(r'^老?([1-5])王?$')
_rex2_bcode = re.compile(r'^老?([一二三四五])王?$')
_rex_rcode = re.compile(r'^[1-9]\d{0,2}$')

def damage_int(x:str) -> int:
    x = util.normalize_str(x)
    if m := _rex_dint.match(x):
        x = int(m.group(1)) * _unit_rate[m.group(2).lower()]
        if x < 100000000:
            return x
    raise ParseError('伤害值不合法 伤害值应为小于一亿的非负整数')


def boss_code(x:str) -> int:
    x = util.normalize_str(x)
    if m := _rex1_bcode.match(x):
        return int(m.group(1))
    elif m := _rex2_bcode.match(x):
        return '零一二三四五'.find(m.group(1))
    raise ParseError('Boss编号不合法 应为1-5的整数')


def round_code(x:str) -> int:
    x = util.normalize_str(x)
    if _rex_rcode.match(x):
        return int(x)
    raise ParseError('周目数不合法 应为不大于999的非负整数')


def server_code(x:str) -> int:
    x = util.normalize_str(x)
    if x in ('jp', '日', '日服'):
        return BattleMaster.SERVER_JP
    elif x in ('tw', '台', '台服'):
        return BattleMaster.SERVER_TW
    elif x in ('cn', '国', '国服', 'b', 'b服'):
        return BattleMaster.SERVER_CN
    raise ParseError('未知服务器地区 请用jp/tw/cn')


def server_name(x:int) -> str:
    if x == BattleMaster.SERVER_JP:
        return 'jp'
    elif x == BattleMaster.SERVER_TW:
        return 'tw'
    elif x == BattleMaster.SERVER_CN:
        return 'cn'
    else:
        return 'unknown'

__all__ = [
    'damage_int', 'boss_code', 'round_code', 'server_code', 'server_name'
]
