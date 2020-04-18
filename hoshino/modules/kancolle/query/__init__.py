from hoshino.res import R
from hoshino.service import Service

sv = Service('kc-query', enable_on_default=False)

from .fleet import *
from .senka import *


# @sv.on_command('菱饼任务', only_to_me=False)
# async def hishimochi(session):
#     msg = R.img('kancolle/quick/菱饼2020.jpg').cqcode
#     await session.send(msg, at_sender=True)
