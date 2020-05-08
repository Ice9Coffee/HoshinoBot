from . import sv
from hoshino import R, CommandSession, util


p1 = R.img('priconne/quick/qian.png').cqcode
p2 = R.img('priconne/quick/zhong.png').cqcode
p3 = R.img('priconne/quick/hou.png').cqcode
@sv.on_rex(r'^([前中后])?rank', normalize=True, event='group')
async def rank_sheet(bot, ctx, match):
    is_qian = match.group(1) == '前'
    is_zhong = match.group(1) == '中'
    is_hou = match.group(1) == '后'
    if not is_qian and not is_hou and not is_zhong:
        await bot.send(ctx, '\n请问您要查台服前中后卫哪个的rank表？\n前rank\n后rank\n中rank', at_sender=True)
    else:
        await bot.send(ctx, '图片较大，请稍等片刻')
        if is_qian:
            await bot.send(ctx, f'台服前卫rank表：\n{p1}\nby 无羽', at_sender=True)
            await util.silence(session.ctx, 60)
        if is_zhong:
            await bot.send(ctx, f'台服中卫rank表：\n{p2}\nby 无羽', at_sender=True)
            await util.silence(session.ctx, 60)
        if is_hou:
            await bot.send(ctx, f'台服后卫rank表：\n{p3}\nby 无羽', at_sender=True)
            await util.silence(session.ctx, 60)


@sv.on_command('arena_miner', aliases=('挖矿', 'jjc钻石', '竞技场钻石', 'jjc钻石查询', '竞技场钻石查询'))
async def arena_miner(session: CommandSession):
    try:
        rank = int(session.current_arg_text)
    except:
        session.finish(f'请输入"挖矿 纯数字最高排名"', at_sender=True)
    if (rank > 15000):
        amount = 42029
    elif (rank > 12000):
        amount = (rank / 100 - 120) * 45 + 40679
    elif (rank > 11900):
        amount = 40599
    elif (rank > 7999):
        amount = (rank / 100 - 80) * 95 + 36799
    elif (rank > 4000):
        amount = (rank - 4001) + 32800
    elif (rank > 2000):
        amount = (rank - 2001) * 3 + 26800
    elif (rank > 1000):
        amount = (rank - 1001) * 5 + 21800
    elif (rank > 500):
        amount = (rank - 501) * 7 + 18300
    elif (rank > 200):
        amount = (rank - 201) * 13 + 14400
    elif (rank > 100):
        amount = (rank - 101) * 35 + 10900
    elif (rank > 10):
        amount = (rank - 11) * 60 + 5500
    elif (rank > 0):
        amount = (rank - 1) * 550
    else:
        amount = 0
    amount = int(amount)
    messages = f"矿里还剩{amount}钻石"
    await session.send(messages, at_sender=True)

p4 = R.img('priconne/quick/brank.jpg').cqcode
brank_url = 'http://news.17173.com/z/gzlj/content/04202020/153933439.shtml'
@sv.on_command('brank', aliases=('Brank', 'BRANK', '国服rank', 'bcrrank', 'B服rank'))
async def brank(session: CommandSession):
    await session.send('图片较大，请稍等片刻',)
    await session.send(f'B服rank表:\n{p4}\nfrom 17173\n原文链接: {brank_url}', at_sender=True)
    await util.silence(session.ctx, 60)

yukari_pic = R.img('priconne/quick/yukari.jpg').cqcode
YUKARI_SHEET = f'''
{yukari_pic}
※大圈是1动充电对象 PvP测试
※黄骑四号位例外较多
※对面羊驼或中后卫坦 有可能歪
※我方羊驼算一号位'''
@sv.on_command('yukari_charge', aliases=('黄骑充电', '黄骑充电表', '酒鬼充电', '酒鬼充电表'))
async def yukari(session: CommandSession):
    await session.send('图片较大，请稍等片刻',)
    await session.send(YUKARI_SHEET, at_sender=True)
    await util.silence(session.ctx, 60)

@sv.on_command('star',aliases=('星级表','升星表'))
async def star(session: CommandSession):
    await session.send(R.img('priconne/quick/star.jpg').cqcode, at_sender=True)
    await util.silence(session.ctx, 60)
