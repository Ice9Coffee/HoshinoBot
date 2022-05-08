import asyncio
import os
from typing import Iterable

import nonebot
from aiocqhttp import Event as CQEvent
from nonebot import message_preprocessor
from nonebot.message import CanceledException


class HoshinoBot(nonebot.NoneBot):
    def __init__(self, config_object=None):
        '''
        You should NOT instantiate a HoshinoBot!
        This is for intellisense code completion.
        Use `hoshino.init()` instead.
        '''
        super().__init__(config_object)
        raise Exception("You should NOT instantiate a HoshinoBot! Use `hoshino.init()` instead.")

    @staticmethod
    def get_self_ids() -> Iterable[str]:
        return get_self_ids()

    @staticmethod
    def finish(event, message, **kwargs):
        if message:
            bot = get_bot()
            asyncio.run_coroutine_threadsafe(bot.send(event, message, **kwargs), bot.loop)
        raise CanceledException('ServiceFunc of HoshinoBot finished.')

    @staticmethod
    async def silence(ev: CQEvent, ban_time, skip_su=True):
        return await util.silence(ev, ban_time, skip_su)


from .service import Service, sucmd
from . import config, log, util

__all__ = [
    'HoshinoBot',
    'Service',
    'sucmd',
    'get_bot',
    'message_preprocessor',
]

_bot = None
logger = log.new_logger('hoshino', config.DEBUG)


def init() -> HoshinoBot:
    global _bot
    nonebot.init(config)
    _bot = nonebot.get_bot()
    _bot.get_self_ids = HoshinoBot.get_self_ids
    _bot.finish = HoshinoBot.finish
    _bot.silence = HoshinoBot.silence

    nonebot.logger.addHandler(log.error_handler)
    nonebot.logger.addHandler(log.critical_handler)

    # Hoshino User Data
    os.makedirs(os.path.expanduser('~/.hoshino'), exist_ok=True)

    for module_name in config.MODULES_ON:
        nonebot.load_plugins(
            os.path.join(os.path.dirname(__file__), 'modules', module_name),
            f'hoshino.modules.{module_name}')

    from . import msghandler

    return _bot


def get_bot() -> HoshinoBot:
    if _bot is None:
        raise ValueError('HoshinoBot has not been initialized')
    return _bot


def get_self_ids() -> Iterable[str]:
    return list(get_bot()._wsr_api_clients.keys())
