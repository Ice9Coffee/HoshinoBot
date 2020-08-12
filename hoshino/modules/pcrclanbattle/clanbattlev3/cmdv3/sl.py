from datetime import datetime
from hoshino import Service, priv
from hoshino.typing import *

from ..battlemaster import BattleMaster as Master
from ..const import *
from ..model import *
from ..dtype import *

from . import sv


@sv.on_fullmatch('sl')
async def log_sl(bot, ev):
    pass

