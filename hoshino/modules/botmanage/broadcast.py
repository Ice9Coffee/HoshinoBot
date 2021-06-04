import asyncio

import hoshino
from hoshino.service import sucmd
from hoshino.typing import CommandSession, CQHttpError


@sucmd('broadcast', aliases=('bc', '广播'), force_private=False)
async def broadcast(session: CommandSession):
    msg = session.current_arg
    bot = session.bot
    ev = session.event
    su = session.event.user_id
    for sid in hoshino.get_self_ids():
        gl = await bot.get_group_list(self_id=sid)
        gl = [g['group_id'] for g in gl]
        await bot.send_private_msg(self_id=sid, user_id=su, message=f"开始向{len(gl)}个群广播：\n{msg}")
        for g in gl:
            await asyncio.sleep(0.5)
            try:
                await bot.send_group_msg(self_id=sid, group_id=g, message=msg)
                hoshino.logger.info(f'群{g} 投递广播成功')
            except CQHttpError as e:
                hoshino.logger.error(f'群{g} 投递广播失败：{type(e)}')
                try:
                    await bot.send_private_msg(self_id=sid, user_id=su, message=f'群{g} 投递广播失败：{type(e)}')
                except Exception as e:
                    hoshino.logger.critical(f'向广播发起者进行错误回报时发生错误：{type(e)}')
    await bot.send_private_msg(self_id=ev.self_id, user_id=su, message='广播完成！')
