import random
from datetime import timedelta

import nonebot
from nonebot import on_command, message_preprocessor, Message, MessageSegment
from nonebot.message import _check_calling_me_nickname
try:        # TODO: drop support for nonebot v1.5
    from nonebot.command import parse_command
except:     # TODO: bump dependence to nonebot v1.6
    from nonebot.command import CommandManager
    parse_command = CommandManager().parse_command

from hoshino import logger, util, Service, R

bot = nonebot.get_bot()
BLANK_MESSAGE = Message(MessageSegment.text(''))

@message_preprocessor
async def black_filter(bot, ctx, plugin_manager=None):  # plugin_manager is new feature of nonebot v1.6
    first_msg_seg = ctx['message'][0]
    if first_msg_seg.type == 'hb':
        return  # pass normal Luck Money Pack to avoid abuse
    if ctx['message_type'] == 'group' and Service.check_block_group(ctx['group_id']) \
       or Service.check_block_user(ctx['user_id']):
        ctx['message'] = BLANK_MESSAGE


def _check_hbtitle_is_cmd(ctx, title):
    ctx = ctx.copy()    # 复制一份，避免影响原有的ctx
    ctx['message'] = Message(title)
    _check_calling_me_nickname(bot, ctx)
    cmd, _ = parse_command(bot, str(ctx['message']).lstrip())
    return bool(cmd)


@bot.on_message('group')
async def hb_handler(ctx):
    self_id = ctx['self_id']
    user_id = ctx['user_id']
    group_id = ctx['group_id']
    first_msg_seg = ctx['message'][0]
    if first_msg_seg.type == 'hb':
        title = first_msg_seg['data']['title']
        if _check_hbtitle_is_cmd(ctx, title):
            Service.set_block_group(group_id, timedelta(hours=1))
            Service.set_block_user(user_id, timedelta(days=30))
            util.silence(ctx, 7 * 24 * 60 * 60)
            msg_from = f"{ctx['user_id']}@[群:{ctx['group_id']}]"
            logger.critical(f'Self: {ctx["self_id"]}, Message {ctx["message_id"]} from {msg_from} detected as abuse: {ctx["message"]}')
            await bot.send(ctx, "检测到滥用行为，您的操作已被记录并加入黑名单。\nbot拒绝响应本群消息1小时", at_sender=True)
            try:
                await bot.set_group_kick(self_id=self_id, group_id=group_id, user_id=user_id, reject_add_request=True)
                logger.critical(f"已将{user_id}移出群{group_id}")
            except:
                pass


# ============================================ #

BANNED_WORD = (
    'rbq', 'RBQ', '憨批', '废物', '死妈', '崽种', '傻逼', '傻逼玩意', 
    '没用东西', '傻B', '傻b', 'SB', 'sb', '煞笔', 'cnm', '爬', 'kkp', 
    'nmsl', 'D区', '口区', '我是你爹', 'nmbiss', '弱智', '给爷爬', '杂种爬'
)
@on_command('ban_word', aliases=BANNED_WORD, only_to_me=True)
async def ban_word(session):
    ctx = session.ctx
    user_id = ctx['user_id']
    msg_from = str(user_id)
    if ctx['message_type'] == 'group':
        msg_from += f'@[群:{ctx["group_id"]}]'
    elif ctx['message_type'] == 'discuss':
        msg_from += f'@[讨论组:{ctx["discuss_id"]}]'
    logger.critical(f'Self: {ctx["self_id"]}, Message {ctx["message_id"]} from {msg_from}: {ctx["message"]}')
    # await session.send(random.choice(BANNED_WORD))
    Service.set_block_user(user_id, timedelta(hours=8))
    pic = R.img(f"chieri{random.randint(1, 4)}.jpg").cqcode
    await session.send(f"不理你啦！バーカー\n{pic}", at_sender=True)
    await util.silence(session.ctx, 8*60*60)
