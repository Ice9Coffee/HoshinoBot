from nonebot import CommandSession
import nonebot.permission as perm

from hoshino.service import Service
from hoshino.log import logger

sv = Service('TestService', 0, 0)

@sv.on_command('svTest', permission=perm.SUPERUSER)
async def svTest(session:CommandSession):
    logger.info('svTestCalled')
    await session.send('svTest Called.')
