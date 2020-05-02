import random
from datetime import timedelta

from nonebot import on_command
from hoshino import util
from hoshino.res import R
from hoshino.service import Service, Privilege as Priv
from hoshino.util import DailyNumberLimiter

_max_yaofan = 10
_limit_yaofan = DailyNumberLimiter(_max_yaofan)

# basic function for debug, not included in Service('chat')
@on_command('zai?', aliases=('在?', '在？', '在吗', '在么？', '在嘛', '在嘛？'))
async def say_hello(session):
    await session.send('はい！私はいつも貴方の側にいますよ！')

sv = Service('chat', manage_priv=Priv.SUPERUSER, visible=False)

@sv.on_command('沙雕机器人', aliases=('沙雕機器人',), only_to_me=False)
async def say_sorry(session):
    await session.send('ごめんなさい！嘤嘤嘤(〒︿〒)')

@sv.on_command('老婆', aliases=('waifu', 'laopo'), only_to_me=True)
async def chat_waifu(session):
    if not sv.check_priv(session.ctx, Priv.SUPERUSER):
        await session.send(R.img('laopo.jpg').cqcode)
    else:
        await session.send('mua~')

@sv.on_command('老公', only_to_me=True)
async def chat_laogong(session):
    await session.send('你给我滚！', at_sender=True)

@on_command('妈?', aliases=('妈', '妈妈', '母亲', '妈!', '妈！', '妈妈！'))
async def say_erzi(session):
    uid = session.ctx['user_id']
    if not _limit_yaofan.check(uid):
        await session.send('今天已经给过你了，不要再要饭了！')
    else:
        _limit_yaofan.increase(uid)
        mana = random.randint(10, 10000000)
        todo = random.randint(0, len(todo_list) - 1)
        await session.send('乖孩子，这是给你的零花钱！\n获得：' + format(mana, ',') + ' 玛那\n你打算去' + todo_list[todo], at_sender=True)

@sv.on_command('mua', only_to_me=True)
async def chat_mua(session):
    await session.send('笨蛋~', at_sender=True)

@sv.on_command('来点星奏', only_to_me=False)
async def seina(session):
    await session.send(R.img('星奏.png').cqcode)

@sv.on_command('我有个朋友说他好了', aliases=('我朋友说他好了', ), only_to_me=False)
async def ddhaole(session):
    await session.send('那个朋友是不是你弟弟？')
    await util.silence(session.ctx, 30)

@sv.on_command('我好了', only_to_me=False)
async def nihaole(session):
    await session.send('不许好，憋回去！')
    await util.silence(session.ctx, 30)

# ============================================ #

@sv.on_keyword(('确实', '有一说一', 'u1s1', 'yysy'))
async def chat_queshi(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img('确实.jpg').cqcode)

@sv.on_keyword(('会战', '刀'))
async def chat_clanba(bot, ctx):
    if random.random() < 0.03:
        await bot.send(ctx, R.img('我的天啊你看看都几点了.jpg').cqcode)

@sv.on_keyword(('内鬼'))
async def chat_neigui(bot, ctx):
    if random.random() < 0.10:
        await bot.send(ctx, R.img('内鬼.png').cqcode)


todo_list = [
        '找老师上课',
        '给宫子买布丁',
        '和真琴一起捡垃圾',
        '找镜哥探讨女装',
        '跟团长一起GBF',
        '迫害优衣',
        '解救挂树的队友',
        '来一发十连',
        '井一发当期的限定池',
        '给妈妈买一束康乃馨',
        '充值b站大会员',
        '买一部最新款的X为手机',
        '购买黄金保值',
        'py竞技场上的大佬',
        '给别的女人打钱',
        '充一笔518',
        '努力工作，尽早报答妈妈的养育之恩',
        '买最新款的海王星',
        '合一套天空',
        '试玩国产塞尔达',
        '二龙路圣地巡礼',
        '做一套大保健',
        '成为魔法少女',
        '搓一把日麻'
    ]