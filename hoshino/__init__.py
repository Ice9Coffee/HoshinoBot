import os

import nonebot
from nonebot.message import CanceledException
from nonebot import Message, MessageSegment, message_preprocessor

HoshinoBot = nonebot.NoneBot

from . import log, config, util
from .service import Service, sucmd

__version__ = '2.2.0'

_bot = None
os.makedirs(os.path.expanduser('~/.hoshino'), exist_ok=True)
logger = log.new_logger('hoshino', config.DEBUG)

def init() -> HoshinoBot:
    global _bot
    nonebot.init(config)
    _bot = nonebot.get_bot()
    _bot.finish = _finish
    _bot.get_self_ids = get_self_ids
    _bot.silence = util.silence

    from .log import error_handler, critical_handler
    nonebot.logger.addHandler(error_handler)
    nonebot.logger.addHandler(critical_handler)

    for module_name in config.MODULES_ON:
        nonebot.load_plugins(
            os.path.join(os.path.dirname(__file__), 'modules', module_name),
            f'hoshino.modules.{module_name}')

    from . import msghandler

    return _bot


async def _finish(event, message, **kwargs):
    if message:
        await _bot.send(event, message, **kwargs)
    raise CanceledException('ServiceFunc of HoshinoBot finished.')


def get_bot() -> HoshinoBot:
    if _bot is None:
        raise ValueError('HoshinoBot has not been initialized')
    return _bot


def get_self_ids():
    if _bot is None:
        raise ValueError('HoshinoBot has not been initialized')
    return _bot._wsr_api_clients.keys()
