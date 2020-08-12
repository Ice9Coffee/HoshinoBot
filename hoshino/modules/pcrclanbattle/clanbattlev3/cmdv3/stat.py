from hoshino.typing import *

from ..battlemaster import BattleMaster as Master
from ..const import *
from ..model import *
from ..dtype import *
from ..helper import *

from . import sv

@sv.on_fullmatch("统计")
async def stat(bot, ev):
    pass


@sv.on_fullmatch("查刀")
async def list_remain(bot, ev):
    pass


@sv.on_fullmatch("催刀")
async def urge_remain(bot, ev):
    pass


@sv.on_prefix("离职报告")
async def retire_report(bot, ev):
    pass
