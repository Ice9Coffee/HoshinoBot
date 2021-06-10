from nonebot.message import CanceledException, message_preprocessor

from ._interact import interact, ActSession
from hoshino import logger
from hoshino.typing import CQEvent, HoshinoBot


@message_preprocessor
async def handler_interaction(bot: HoshinoBot, ev: CQEvent, _):
    if interact.find_session(ev):
        session = interact.find_session(ev)

        if ev.raw_message == 'exit' and ev.user_id == session.creator:  # 创建者选择退出
            session.close()
            await session.finish(ev, f'{session.name}已经结束，欢迎下次再玩！')

        if session.is_expire():
            session.close()
            await bot.send(ev, f'时间已到，{session.name}自动结束')

        func = session.actions.get(ev.raw_message) if ev.user_id in session.users else None

        if func:
            logger.info(f'triggered interaction action {func.__name__}')
            try:
                await func(ev, session)
            except CanceledException as e:
                logger.info(e)
            except Exception as ex:
                logger.exception(ex)
            raise CanceledException('handled by interact handler')
        elif session.handle_msg:
            await session.handle_msg(ev, session)
        else:
            pass
