from datetime import datetime
from hoshino import Service, priv
from hoshino.typing import *

from ..battlemaster import BattleMaster as Master
from ..const import *
from ..model import *
from ..dtype import *
from . import sv

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
