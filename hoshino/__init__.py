import os
from os import path 
import logging
import nonebot

os.makedirs(os.path.expanduser('~/.hoshino'), exist_ok=True)
from .log import logger

def init(config) -> nonebot.NoneBot:

    nonebot.init(config)
    bot = nonebot.get_bot()

    from .log import error_handler, critical_handler
    logger.setLevel(logging.DEBUG if bot.config.DEBUG else logging.INFO)
    nonebot.logger.setLevel(logging.DEBUG if bot.config.DEBUG else logging.INFO)
    nonebot.logger.addHandler(error_handler)
    nonebot.logger.addHandler(critical_handler)

    for module_name in config.MODULES_ON:
        nonebot.load_plugins(
            path.join(path.dirname(__file__), 'modules', module_name),
            f'hoshino.modules.{module_name}'
        )

    return bot


def get_bot() -> nonebot.NoneBot:
    return nonebot.get_bot()


from nonebot import NoneBot, CommandSession, MessageSegment

from .service import Service, Privilege
from .res import R
