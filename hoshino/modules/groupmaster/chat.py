import random

from hoshino import util
from hoshino.res import R
from hoshino.service import Service, Privilege as Priv

sv = Service('chat', manage_priv=Priv.SUPERUSER, enable_on_default=True, visible=False)

@sv.on_command('sayhello', aliases=('在', '在？', '在吗', '在么？', '在嘛', '在嘛？'))
async def say_hello(session):
    await session.send('はい！私はいつも貴方の側にいますよ！')

@sv.on_command('沙雕机器人', aliases=('沙雕機器人',), only_to_me=False)
async def say_sorry(session):
    await session.send('ごめんなさい！嘤嘤嘤(〒︿〒)')

@sv.on_command('老婆', aliases=('waifu', 'laopo'))
async def _(session):
    if not await sv.check_permission(session.ctx, Priv.SUPERUSER):
        await session.send(R.img('喊谁老婆呢.jpg').cqcode)
    else:
        await session.send('mua~')

@sv.on_command('mua')
async def _(session):
    await session.send('笨蛋~')


@sv.on_keyword({'确实', '有一说一', 'u1s1', 'yysy'}, normalize=True)
async def _(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img('确实.jpg').cqcode)

@sv.on_keyword({'会战', '刀'}, normalize=True)
async def _(bot, ctx):
    if random.random() < 0.03:
        await bot.send(ctx, R.img('我的天啊你看看都几点了.jpg').cqcode)

@sv.on_keyword({'内鬼'}, normalize=True)
async def _(bot, ctx):
    if random.random() < 0.10:
        await bot.send(ctx, R.img('内鬼.png').cqcode)


BANNED_WORD = ('rbq', 'RBQ', '憨批', '废物', '死妈', '崽种', '傻逼', '傻逼玩意', '没用东西', '傻B', '傻b', 'SB', 'sb', '煞笔', 'cnm', '爬', 'kkp', 'nmsl', 'D区', '口区', '我是你爹')
@sv.on_command('ban_word', aliases=BANNED_WORD, only_to_me=True)
async def ban_word(session):
    ctx = session.ctx
    msg_from = str(ctx['user_id'])
    if ctx['message_type'] == 'group':
        msg_from += f'@[群:{ctx["group_id"]}]'
    elif ctx['message_type'] == 'discuss':
        msg_from += f'@[讨论组:{ctx["discuss_id"]}]'
    sv.logger.critical(f'Self: {ctx["self_id"]}, Message {ctx["message_id"]} from {msg_from}: {ctx["message"]}')
    await session.send(random.choice(BANNED_WORD), at_sender=True)
    await util.silence(session.ctx, 24*60*60)
