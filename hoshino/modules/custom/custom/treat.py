
import random
from hoshino import R, CommandSession
from . import sv1

qks_url = ["granbluefantasy.jp"]
qksimg = R.img('priconne/quick/qksimg.jpg').cqcode
xiaobao_aliases = ('迫害奉孝', '迫害孝宝')
bbl_aliases = ('迫害bbl', '迫害芭芭拉')
xbimg1 = R.img('priconne/quick/xiaobao.png').cqcode
bblimg = R.img('priconne/quick/bbl.png').cqcode
xbimg2 = R.img('priconne/quick/xiaobao1.png').cqcode
qks_url = ["granbluefantasy.jp"]
qksimg = R.img('priconne/quick/qksimg.jpg').cqcode
nothing = R.img('priconne/quick/我什么都没有.png').cqcode
prof = R.img('priconne/quick/专业团队.png').cqcode
longtree = R.img('priconne/quick/大树.jpg').cqcode
shorttree = R.img('priconne/quick/小树.jpg').cqcode
multisp=R.img('priconne/quick/多人运动.jpg').cqcode

@sv1.on_keyword(qks_url, normalize=True, event='group')
async def qks(bot, ctx):
    msg = f'爪巴\n{qksimg}'
    await bot.send(ctx, msg, at_sender=True)


@sv1.on_command('xiaobao', aliases=xiaobao_aliases, only_to_me=False)
async def xiaobao(session: CommandSession):
    a = random.randint(1, 100)
    if a <= 50:
        await session.send(f'您又迫害孝宝了！孝宝要哭了\n{xbimg1}', at_sender=True)
    else:
        await session.send(f'您又迫害孝宝了！孝宝要哭了\n{xbimg2}', at_sender=True)


@sv1.on_command('bbl', aliases=bbl_aliases, only_to_me=False)
async def bbl(session: CommandSession):
    await session.send(f'不要这样啊！你们不要再迫害bbl了呀！\n{bblimg}', at_sender=True)


@sv1.on_keyword(('我什么都没有'))
async def havenothing(bot, ctx):
    a = random.randint(1, 100)
    if a <= 10:
        await bot.send(ctx,f'{nothing}')


@sv1.on_command('professional', aliases=('专业团队', '黑人抬棺'), only_to_me=False)
async def profe(session: CommandSession):
    await session.send(f'{prof}')


@sv1.on_command('duorenyundong', aliases=('多人运动','三人忘刀'), only_to_me=False)
async def multisport(session: CommandSession):
    await session.send(f'{multisp}')


@sv1.on_keyword(('挂树', '查树'))
async def tree(bot, ctx):
    a = random.randint(1, 1000)
    if a <= 10:
        await bot.send(ctx,f'{longtree}')
    elif a <= 110:
        await bot.send(ctx,f'{shorttree}')
