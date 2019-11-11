
import base64
from io import BytesIO
from PIL import Image

from nonebot import get_bot
from nonebot import CommandSession
from nonebot import permission as perm
from aiocqhttp.exceptions import ActionFailed

from .log import logger

async def delete_msg(session:CommandSession):
    try:
        if get_bot().config.IS_CQPRO:
            msg_id = session.ctx['message_id']
            await session.bot.delete_msg(message_id=msg_id)
    except ActionFailed as e:
        logger.error(f'撤回失败 retcode={e.retcode}')


async def silence(session:CommandSession, ban_time, ignore_super_user=False):
    try:
        group_id = session.ctx['group_id']
        user_id = session.ctx['user_id']
        if ignore_super_user or not await perm.check_permission(session.bot, session.ctx, perm.SUPERUSER):
            await session.bot.set_group_ban(group_id=group_id, user_id=user_id, duration=ban_time)
    except ActionFailed as e:
        logger.error(f'禁言失败 retcode={e.retcode}')


def pic2b64(pic:Image) -> str:
    buf = BytesIO()
    pic.save(buf, format='PNG')
    base64_str = str(base64.b64encode(buf.getvalue()), encoding='utf8')
    return f'base64://{base64_str}'


def concat_pic(pics, border=5):
    num = len(pics)
    w, h = pics[0].size
    des = Image.new('RGBA', (w, num * h + (num-1) * border), (255, 255, 255, 255))
    for i, pic in enumerate(pics):
        des.paste(pic, (0, i * (h + border)), pic)
    return des
