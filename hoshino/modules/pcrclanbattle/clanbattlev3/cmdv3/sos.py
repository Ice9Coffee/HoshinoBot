from datetime import datetime
from hoshino import Service, priv
from hoshino.typing import *

from ..battlemaster import BattleMaster as Master
from ..const import *
from ..model import *
from ..dtype import *
from . import sv


@sv.on_fullmatch(('挂树', '上树'))
async def add_sos(bot, ev):
    pass


@sv.on_fullmatch('查树')
async def list_sos(bot, ev):
    pass


