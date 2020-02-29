from datetime import timedelta

import nonebot
from nonebot import message_preprocessor, Message, MessageSegment
from nonebot.command import parse_command
from nonebot.message import _check_calling_me_nickname

from hoshino import util
from hoshino.log import logger
from hoshino.service import Service

bot = nonebot.get_bot()
BLANK_MESSAGE = Message(MessageSegment.text(''))

@message_preprocessor
async def black_list(bot, ctx):
    if ctx['message_type'] == 'group' and Service.check_block_group(ctx['group_id']):
        ctx['message'] = BLANK_MESSAGE


def _check_hbtitle_is_cmd(ctx, title):
    ctx = ctx.copy()    # 复制一份，避免影响原有的ctx
    ctx['message'] = Message(title)
    _check_calling_me_nickname(bot, ctx)
    cmd, _ = parse_command(bot, str(ctx['message']).lstrip())
    return bool(cmd)


@bot.on_message('group')
async def hb_handler(ctx):
    group_id = ctx['group_id']
    first_msg_seg = ctx['message'][0]
    if first_msg_seg.type == 'hb':
        title = first_msg_seg['data']['title']
        if _check_hbtitle_is_cmd(ctx, title):
            Service.set_block_group(group_id, timedelta(hours=1))
            util.silence(ctx, 7 * 24 * 60 * 60)
            msg_from = f"{ctx['user_id']}@[群:{ctx['group_id']}]"
            logger.critical(f'Self: {ctx["self_id"]}, Message {ctx["message_id"]} from {msg_from} detected as abuse: {ctx["message"]}')
            await bot.send(ctx, "检测到滥用行为，您的操作已被记录。\nbot拒绝响应本群消息1小时", at_sender=True)
