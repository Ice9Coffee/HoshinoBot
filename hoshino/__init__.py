from os import path 
import logging

import nonebot

from .log import logger


MODULES_ON = {
    'priconne',
    'groupmaster',
    'subscribe',
    'translate',
    'setu',
}


def init(config) -> nonebot.NoneBot:

    nonebot.init(config)
    bot = nonebot.get_bot()

    logger.setLevel(logging.DEBUG if bot.config.DEBUG else logging.INFO)

    for module_name in MODULES_ON:
        nonebot.load_plugins(
            path.join(path.dirname(__file__), 'modules', module_name),
            f'hoshino.modules.{module_name}'
        )

    return bot
