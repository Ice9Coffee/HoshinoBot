from nonebot import *
import json
from random import randint
import asyncio
import random
import os
import hoshino
from hoshino import R, Service, priv, util

bot = get_bot()
fd = os.path.dirname(__file__)

with open(os.path.join(fd, 'rsdata.json')) as f:
    data = json.load(f)
with open(os.path.join(fd, 'rsplayer.json')) as f:
    player = json.load(f)


def save(data, file):
    with open(file, 'w') as f:
        json.dump(data, f)


sv_help = '''
- [开枪] 俄罗斯轮盘游戏
'''.strip()

sv = Service(
    name='俄罗斯轮盘游戏',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 是否可见
    enable_on_default=True,  # 是否默认启用
    bundle='娱乐',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助-俄罗斯轮盘游戏"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


# main part
@sv.on_command('rs', aliases=('俄罗斯轮盘', '开枪'), only_to_me=False)
async def spin(session: CommandSession):
    ydie = [
        "很不幸，你死了......",
        "You Die...",
        "你拿着手枪掂了掂，你赌枪里没有子弹\n\n然后很不幸，你死了...",
        "你是一个有故事的人，但是子弹并不想知道这些，它只看见了白花花的脑浆\n\n你死了",
        "你没有想太多，扣下了扳机。你感觉到有什么东西从你的旁边飞过，然后意识陷入了黑暗\n\n你死了",
        "大多数人对自己活着并不心存感激，但你不再是了\n\nYou Die...",
        "你举起了枪又放下，然后又举了起来，你的内心在挣扎，但是你还是扣下了扳机\n\nYou Die...",
        "黄澄澄的子弹穿过了你的大脑，一声枪响之后你倒在了地上，我把你送去了医院\n\n你很幸运，你并没有死。只是你陷入了一片黑暗，身体也无法动弹。但这也许最大的不幸吧",
        "你开枪之前先去吃了杯泡面\n\n然后很不幸，你死了...",
        "你对此胸有成竹，你曾经在精神病院向一个老汉学习了用手指夹住子弹的功夫\n\n然后很不幸你没夹住手滑了，死了...",
        "今天的风儿很喧嚣，沙尘能让眼睛感到不适。你去揉眼睛的时候手枪走火，贯穿了你的小腹。你血流不止，你呻吟不断，但是在风声中没有人注意到你\n\n然后很不幸，你死了...",
        "今天的风儿很喧嚣，让人站稳都很困难。你扣下了扳机，子弹咆哮着窜出\n\n你失败了，但是你并没有死\n你脚滑了子弹与你擦肩而过，你在风声中逃离了现场\n几天后，你听说那天还有人在风中玩俄罗斯轮盘，你不由感到庆幸",
        "你扣下了扳机\n\nYou Die...",
        "一声轰鸣，强劲的子弹将你的头骨扯碎，就像一颗腐烂后砸在地上的番茄。你下意识地用手摸了一下后脑勺，意识消失前残留在你印象里的是手上的温热\n\nYou Die...",
        "我会死吗?我死了吗？你正这样想着\n\n然后很不幸，你死了...",
        "砰...很不幸，你死了......",
        "漆黑的眩晕中，心脏渐渐窒息无力，彻骨的寒冷将你包围\n\n很不幸，你死了...",
        "很不幸，你死了......",
        "“嘭”，很不幸，你死了...",
        "原本声音是喘息平静是喘息大海是喘息你听见它声音不说话不歌唱也不呼吸一秒两秒数十年百年时间过去它沉默依旧\n\n你死了...",
    ]
    ylive = [
        "你活了下来，下一位",
        "你扣动扳机，无事发生\n\n你活了下来",
        "你自信的扣动了扳机，正如你所想象的那样\n\n你活了下来，下一位",
        "你感觉命运女神在向你招手\n\n然后，你活了下来，下一位",
        "你活下来了，下一位",
        "你吃了杯泡面发现没有调料，你觉得不幸的你恐怕是死定了\n\n然后，你活了下来，下一位",
        "你吃了杯泡面发现没有调料，于是去找老板理论，发现老板已经跑路。感到世态炎凉，人性险恶，打开了你常用的音乐软件，在动人的旋律中对自己扣动了扳机\n\n然后，你活了下来，下一位",
        "人和人的体质不能一概而论，你在极度愤怒下，扣下了扳机。利用扳机扣下和触发子弹的时间差，手指一个加速硬生生扣断了它。\n\n然后，你活了下来，下一位",
        "你对此胸有成竹，你曾经在精神病院向一个老汉学习了用手指夹住子弹的功夫\n\n然后，子弹并没有射出，你活了下来，下一位",
        "你对此胸有成竹，你曾经在精神病院向一个老汉学习过用手指夹住射出子弹的功夫，在子弹射出的一瞬间，你把他塞了回去\n\n你活了下来，下一位",
        "你活了下来，下一位",
        "很不幸，你...不好意思，念错了\n\n你活了下来，下一位",
    ]

    if session.ctx['message_type'] == 'private':
        msg = '此功能仅适用于群聊'
        session.finish(msg)

    else:
        user = str(session.ctx['user_id'])
        group = session.ctx['group_id']
        if group not in player:
            player[group] = {}
        if user not in player[group]:
            player[group][user] = {}
            if len(session.ctx.sender['card']) != 0:
                player[group][user]['nickname'] = session.ctx.sender['card']
            else:
                player[group][user]['nickname'] = session.ctx.sender['nickname']
            player[group][user]['win'] = 0
            player[group][user]['death'] = 0

        if group not in data:
            data[group] = {}
            data[group]['curnum'] = 0
            data[group]['mix'] = 0
            data[group]['next'] = 0

        if data[group]['curnum'] <= 0:
            msg = '欢迎参与紧张刺激的俄罗斯轮盘活动，请输入要填入的子弹数目(最多6颗)'
            bullet = int(session.get('bullet', prompt=msg))
            if bullet == 6:
                ans = session.get('ans', prompt="你认真的？(y/n)")
                if ans == 'y':
                    data[group]['curnum'] = bullet
                    data[group]['mix'] = 0
                    data[group]['next'] = randint(0, 6)
                    await session.send("装填完毕")
                else:
                    session.finish("请重新开始")
            elif bullet < 1 or bullet > 6:
                session.finish("数目不正确，请重新开始.")
            else:
                data[group]['curnum'] = bullet
                data[group]['mix'] = 0
                data[group]['next'] = randint(0, 6)
                await session.send("装填完毕")

        else:
            if data[group]['next'] <= data[group]['curnum']:
                # await session.send("“嘭”，很不幸，你死了...")
                if data[group]['mix'] == 0 and data[group]['curnum'] != 6:
                    await session.send("勇敢而自信的你，率先扣下了扳机\n感受着扳机冰冷的温度，你正像那堂吉诃德，幻想着和强大的对手有着无数次的交锋")
                    await session.send("然后...你死了")
                else:
                    await session.send(random.choice(ydie))
                await util.silence(session.ctx, 1 * 60)
                player[group][user]['death'] += 1
                data[group]['curnum'] -= 1
                data[group]['mix'] += 1
                data[group]['next'] = randint(0, 6 - data[group]['mix'])
                if data[group]['curnum'] <= 0:
                    await session.send("感谢各位的参与，让我们看一下游戏结算:")
                    await asyncio.sleep(1)
                    msg = ''
                    for k, i in player[group].items():
                        msg += (" %s:  胜利: %s   死亡: %s\n" % (i['nickname'], i['win'], i['death']))

                    player[group] = {}
                    data[group]['curnum'] = 0
                    data[group]['mix'] = 0
                    data[group]['next'] = 0

                    player.clear()
                    await session.send(msg)
                else:
                    msg = f"欢迎下一位。已经开了{data[group]['mix']}枪，还剩{data[group]['curnum']}发子弹。"
                    await session.send(msg)
            else:
                data[group]['mix'] += 1
                msg = random.choice(ylive)
                # msg += "你活了下来，下一位.还剩实弹%d发" % data[group]['curnum']
                msg += f"。已经开了{data[group]['mix']}枪，还剩{data[group]['curnum']}发子弹。"
                # msg = f"你活了下来，下一位。已经开了{data[group]['mix']}枪，还剩{data[group]['curnum']}发子弹。" 
                data[group]['next'] = randint(0, 6 - data[group]['mix'])
                player[group][user]['win'] += 1
                await session.send(msg)

        save(data, os.path.join(fd, 'rsdata.json'))
        save(player, os.path.join(fd, 'rsplayer.json'))
