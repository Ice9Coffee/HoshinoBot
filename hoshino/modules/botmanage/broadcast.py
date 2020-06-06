import asyncio

from nonebot import on_command, CommandSession
from nonebot import permission as perm
from nonebot import CQHttpError

from hoshino.log import logger


@on_command('broadcast', aliases=('bc', '广播'), permission=perm.SUPERUSER)
async def broadcast(session:CommandSession):
    msg = session.current_arg
    self_ids = session.bot._wsr_api_clients.keys()
    for sid in self_ids:
        gl = await session.bot.get_group_list(self_id=sid)
        gl = [ g['group_id'] for g in gl ]
        for g in gl:
            await asyncio.sleep(0.5)
            try:
                await session.bot.send_group_msg(self_id=sid, group_id=g, message=msg)
                logger.info(f'群{g} 投递广播成功')
            except CQHttpError as e:
                logger.error(f'Error: 群{g} 投递广播失败 {type(e)}')
                try:
                    await session.send(f'Error: 群{g} 投递广播失败 {type(e)}')
                except CQHttpError as e:
                    logger.critical(f'向广播发起者进行错误回报时发生错误：{type(e)}')
    await session.send(f'广播完成！')
