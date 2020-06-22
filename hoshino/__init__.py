import os
import nonebot

from . import config
from .log import new_logger

_bot = None
HoshinoBot = nonebot.NoneBot
logger = new_logger('hoshino', config.DEBUG)

def check_config():
    assert config.RES_PROTOCOL in ('http', 'file', 'base64')
    config.RES_DIR = os.path.expanduser(config.RES_DIR)


def init() -> HoshinoBot:
    global _bot
    check_config()
    os.makedirs(os.path.expanduser('~/.hoshino'), exist_ok=True)
    nonebot.init(config)
    _bot = nonebot.get_bot()

    from .log import error_handler, critical_handler
    nonebot.logger.addHandler(error_handler)
    nonebot.logger.addHandler(critical_handler)

    for module_name in config.MODULES_ON:
        nonebot.load_plugins(
            os.path.join(os.path.dirname(__file__), 'modules', module_name),
            f'hoshino.modules.{module_name}')

    return _bot


def get_bot() -> HoshinoBot:
    if _bot is None:
        raise ValueError('HoshinoBot has not been initialized')
    return _bot


def get_self_ids():
    return _bot._wsr_api_clients.keys()


from nonebot import message_preprocessor
from nonebot.message import CanceledException

from .res import R
from .service import Service
