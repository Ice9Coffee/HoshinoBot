import os
import re
import random
from nonebot import on_command
from datetime import datetime
import pytz

import hoshino
from hoshino import R, Service, priv, util
from hoshino.typing import CQEvent

tz = pytz.timezone('Asia/Shanghai')

sv_help = """
 回复项
"""

sv = Service(
    name='BotChat',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 是否可见
    enable_on_default=True,  # 是否默认启用
    bundle='娱乐',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


# =====人格=====#
@sv.on_keyword(('沙雕机器人', '笨蛋机器人', '傻逼机器人', '憨憨机器人', '憨批机器人'))
async def chat_sad(bot, ev):
    await bot.send(ev, '哼！你才是笨蛋呢', at_sender=True)


@sv.on_fullmatch('老公', only_to_me=True)
async def chat_laogong(bot, ev):
    await bot.send(ev, '人不能，至少不应该', at_sender=True)


@sv.on_fullmatch('mua', only_to_me=True)
async def chat_mua(bot, ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '这位先生，请控制好自己的行为', at_sender=True)
    else:
        await bot.send(ev, '欸嘿嘿~这么多人有点不好意思呢')


@sv.on_fullmatch(('早安', '早安哦', '早上好', '早上好啊', '早上好呀', '早', 'good morning'))
async def goodmorning(bot, ev):
    # path = './res/bot/早安.mp3'
    now_hour = datetime.now(tz).hour
    if 0 <= now_hour < 6:
        await bot.send(ev, f'好早，现在才{now_hour}点呢', at_sender=True)
    elif 6 <= now_hour < 10:
        await bot.send(ev, '早上好！今天打算做什么呢？', at_sender=True)
        # await bot.send(ev, f'[CQ:record,file=file:///{path}]')
    elif 21 <= now_hour < 24:
        await bot.send(ev, '别闹，准备睡觉啦！', at_sender=True)
    else:
        await bot.send(ev, f'{now_hour}点了才起床吗…', at_sender=True)


@sv.on_fullmatch(('晚上好', '晚上好啊', '晚上好呀', 'good evening'))
async def goodevening(bot, ev):
    now_hour = datetime.now(tz).hour
    # path = './res/bot/晚上好呀。勤劳的青年们有在认真工作嘛.mp3'
    if 18 <= now_hour < 24:
        await bot.send(ev, f'晚上好！今晚想做什么呢？', at_sender=True)
        # await bot.send(ev, f'[CQ:record,file=file:///{path}]')
    elif 0 <= now_hour < 6:
        await bot.send(ev, f'{now_hour}点啦，还不睡吗？', at_sender=True)
    elif 6 <= now_hour <= 9:
        await bot.send(ev, f'晚上好…嗯？我刚起床呢', at_sender=True)
    else:
        await bot.send(ev, f'现在才{now_hour}点，还没天黑呢。嘿嘿', at_sender=True)


@sv.on_fullmatch(('晚安', '晚安哦', '晚安啦', 'good night'))
async def goodnight(bot, ev):
    now_hour = datetime.now(tz).hour
    if now_hour <= 3 or now_hour >= 21:
        await bot.send(ev, '晚安~', at_sender=True)
    elif 19 <= now_hour < 21:
        await bot.send(ev, f'现在才{now_hour}点，这么早就睡了吗？', at_sender=True)
    else:
        await bot.send(ev, f'现在才{now_hour}点，还没到晚上咧。嘿嘿', at_sender=True)


@sv.on_fullmatch(('你真棒', '你好棒', '你真厉害', '你好厉害', '真棒', '真聪明', '你真聪明'), only_to_me=True)
async def iamgood(bot, ev):
    await bot.send(ev, f'诶嘿嘿~')


# ====群聊======#

@sv.on_fullmatch('我好了')
async def ddhaole(bot, ev):
    if random.random() <= 0.50:
        await bot.send(ev, '不许好，憋回去！')
        await util.silence(ev, 30)


@sv.on_keyword('不准套娃')
async def taowa(bot, ev):
    await bot.send(ev, f'不准不准套娃')


@sv.on_fullmatch('我不要你觉得')
async def wojuede(bot, ev):
    await bot.send(ev, f'我要我觉得')


@sv.on_fullmatch('与你无关')
async def yuniwugua(bot, ev):
    await bot.send(ev, f'雨女无瓜')


@sv.on_fullmatch('消除恐惧的最好办法就是面对恐惧')
async def aoligei(bot, ev):
    await bot.send(ev, f'加油，奥利给！')


@sv.on_keyword(('你这瓜', '这瓜'))
async def gua(bot, ev):
    await bot.send(ev, f'这瓜保熟吗？')


@sv.on_keyword(('这是计划的一部分', '这就是我的逃跑路线'))
async def jihua(bot, ev):
    await bot.send(ev, f'这也在你的计划之中吗，JOJO！')


@sv.on_keyword(('大威天龙', '大罗法咒', '准备捉妖', '我一眼就看出你不是人'))
async def nibushiren(bot, ev):
    await bot.send(ev, f'大威天龙\n👌世尊地藏！\n🤙大罗法咒\n🙏般若诸佛！\n✋般若巴麻哄！\n🐉飞龙在天！')


@sv.on_keyword(('兄弟们我做的对吗', '好兄弟们我做的对吗', 'xdm我做的对吗', '我做的对吗', 'hxd们我做的对吗', '兄弟萌我做的对吗', '好兄弟萌我做的对吗', '老铁们我做的对吗'))
async def zhengdaodeguang(bot, ev):
    await bot.send(ev, f'正道的光！照在了大地上~')


@sv.on_keyword(('雷霆嘎巴', '雷霆嘎巴儿'))
async def aa(bot, ev):
    await bot.send(ev, f'无情哈喇少~')


@sv.on_keyword(('你吼那么大声干什么', '你吼辣么大声干什么'))
async def wuguan(bot, ev):
    await bot.send(ev, f'那你去找物管啊')


@sv.on_keyword('这就是你分手的借口')
async def aihe(bot, ev):
    await bot.send(ev,
                   f'🕺🕺🕺如果让你重新来过\n🕺🕺🕺你会不会爱我\n🕺🕺🕺爱情让人拥有快乐\n🕺🕺🕺也会带来折磨\n🕺🕺🕺曾经和你一起走过传说中的爱河\n🕺🕺🕺已经被我泪水淹没\n🕺🕺🕺变成痛苦的爱河')


@sv.on_keyword(('大点声', '大声点', '听不见'))
async def jingshen(bot, ev):
    if random.random() < 0.50:
        await bot.send(ev, '这么小声还想开军舰！？', at_sender=True)
    else:
        await bot.send(ev, '好！很有精神！', at_sender=True)


# 图片请放于 img/bot 目录下 #

@sv.on_keyword(('确实', '有一说一', 'u1s1', 'yysy'))
async def chat_queshi(bot, ev):
    if random.random() < 0.05:
        await bot.send(ev, R.img(f"bot/确实.jpg").cqcode)


@sv.on_keyword(('艹', '草', '操'))
async def chat_queshi(bot, ev):
    if random.random() < 0.05:
        await bot.send(ev, R.img(f"bot/cao.jpg").cqcode)


@sv.on_keyword('内鬼')
async def chat_neigui(bot, ev):
    if random.random() < 0.10:
        await bot.send(ev, R.img(f"bot/内鬼.png").cqcode)


@sv.on_keyword(('上流', '上流社会', '红酒'))
async def chat_clanba(bot, ev):
    if random.random() < 0.10:
        await bot.send(ev, R.img(f"bot/上流.jpg").cqcode)


@sv.on_keyword(('真行', '彳亍'))
async def chat_clanba(bot, ev):
    if random.random() < 0.10:
        await bot.send(ev, R.img(f"bot/行.jpg").cqcode)


@sv.on_keyword(('lsp', '老色批'))
async def chat_clanba(bot, ev):
    if random.random() < 0.10:
        await bot.send(ev, R.img(f"bot/lsp.jpg").cqcode)


@sv.on_keyword(('爬', '爪巴'))
async def chat_clanba(bot, ev):
    if random.random() < 0.05:
        await bot.send(ev, R.img(f"bot/爬.jpg").cqcode)


@sv.on_keyword('不会吧')
async def chat_clanba(bot, ev):
    if random.random() < 0.02:
        await bot.send(ev, R.img(f"bot/不会吧.jpg").cqcode)


@sv.on_keyword(('整一个', '白嫖'))
async def chat_clanba(bot, ev):
    if random.random() < 0.10:
        await bot.send(ev, R.img(f"bot/整一个.png").cqcode)


@sv.on_keyword('正道的光')
async def chat_clanba(bot, ev):
    if random.random() < 0.15:
        await bot.send(ev, R.img(f"bot/正道的光.jpg").cqcode)


@sv.on_keyword(('好臭啊', '野兽先辈'))
async def chat_clanba(bot, ev):
    if random.random() < 0.15:
        await bot.send(ev, R.img(f"bot/臭.jpg").cqcode)


@sv.on_keyword('我超勇的')
async def chat_clanba(bot, ev):
    if random.random() < 0.15:
        await bot.send(ev, R.img(f"bot/勇.jpg").cqcode)


@sv.on_keyword(('你不对劲', '不对劲'))
async def chat_clanba(bot, ev):
    if random.random() < 0.20:
        await bot.send(ev, R.img(f"bot/不对劲.jpg").cqcode)


@sv.on_keyword(('respect', '尊重'))
async def chat_clanba(bot, ev):
    if random.random() < 0.10:
        await bot.send(ev, R.img(f"bot/res.jpg").cqcode)


@sv.on_keyword(('死机', '错误', 'error'))
async def chat_clanba(bot, ev):
    if random.random() < 0.10:
        await bot.send(ev, R.img(f"bot/错误.jpg").cqcode)


@sv.on_keyword(('芜湖', '起飞', '飞飞飞'))
async def chat_clanba(bot, ev):
    if random.random() < 0.10:
        await bot.send(ev, R.img(f"bot/飞.jpg").cqcode)


@sv.on_keyword(('？', '你有问题'))
async def chat_clanba(bot, ev):
    if random.random() < 0.02:
        await bot.send(ev, R.img(f"bot/123.jpg").cqcode)


@sv.on_fullmatch(('我能去你家吃饭嘛', '我能去你家吃饭吗'))
async def chat_clanba(bot, ev):
    if random.random() < 0.20:
        await bot.send(ev, R.img(f"bot/吃饭吃一勺.jpg").cqcode)


@sv.on_keyword(('不太好吧'))
async def chat_clanba(bot, ev):
    if random.random() < 0.15:
        await bot.send(ev, R.img(f"bot/不太好.jpg").cqcode)


@sv.on_keyword(('零花钱'))
async def chat_clanba(bot, ev):
    if random.random() < 0.15:
        await bot.send(ev, R.img(f"bot/零花钱.jpg").cqcode)


@sv.on_fullmatch(('牙白', '牙白的死呐', '厉害了啊', '牙白得死呐'))
async def chat_clanba(bot, ev):
    if random.random() < 0.20:
        await bot.send(ev, R.img(f"bot/牙白.jpg").cqcode)


@sv.on_keyword(('遇到困难', '遇到困难睡大觉'))
async def chat_clanba(bot, ev):
    if random.random() < 0.30:
        await bot.send(ev, R.img(f"bot/遇到困难.jpg").cqcode)


@sv.on_keyword(('云里雾里', '懵', '不懂'))
async def chat_clanba(bot, ev):
    if random.random() < 0.15:
        await bot.send(ev, R.img(f"bot/云里雾里.jpg").cqcode)


# Voice
# @sv.on_fullmatch(('讲话', '说话', '说几句', '说两句'), only_to_me=True)
async def saySomething(bot, ev):
    fileList = os.listdir(R.img(f"bot/").path)
    path = None
    while not path or not os.path.isfile(path):
        filename = random.choice(fileList)
        path = R.img(f"bot/", filename).path
        await bot.send(ev, R.img(f"bot/", filename).cqcode)
