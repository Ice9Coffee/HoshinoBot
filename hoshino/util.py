import unicodedata
import base64
from io import BytesIO
from PIL import Image

import zhconv

from nonebot import get_bot
from aiocqhttp.exceptions import ActionFailed

from .log import logger


async def delete_msg(ctx):
    try:
        if get_bot().config.IS_CQPRO:
            msg_id = ctx['message_id']
            await get_bot().delete_msg(self_id=ctx['self_id'], message_id=msg_id)
    except ActionFailed as e:
        logger.error(f'撤回失败 retcode={e.retcode}')
    except Exception as e:
        logger.exception(e)


async def silence(ctx, ban_time, ignore_super_user=False):
    try:
        self_id = ctx['self_id']
        group_id = ctx['group_id']
        user_id = ctx['user_id']
        bot = get_bot()
        if ignore_super_user or user_id not in bot.config.SUPERUSERS:
            await bot.set_group_ban(self_id=self_id, group_id=group_id, user_id=user_id, duration=ban_time)
    except ActionFailed as e:
        logger.error(f'禁言失败 retcode={e.retcode}')
    except Exception as e:
        logger.exception(e)


def pic2b64(pic:Image) -> str:
    buf = BytesIO()
    pic.save(buf, format='PNG')
    base64_str = base64.b64encode(buf.getvalue()).decode()   #, encoding='utf8')
    return 'base64://' + base64_str


def concat_pic(pics, border=5):
    num = len(pics)
    w, h = pics[0].size
    des = Image.new('RGBA', (w, num * h + (num-1) * border), (255, 255, 255, 255))
    for i, pic in enumerate(pics):
        des.paste(pic, (0, i * (h + border)), pic)
    return des


def normalize_str(string) -> str:
    """
    规范化unicode字符串 并 转为小写 并 转为简体
    """
    string = unicodedata.normalize('NFKC', string)
    string = string.lower()
    string = zhconv.convert(string, 'zh-hans')
    return string
