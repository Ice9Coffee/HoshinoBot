import pytz
from datetime import datetime, timedelta
from collections import defaultdict


from nonebot import on_command, CommandSession, MessageSegment
import nonebot.permission as perm

@on_command('help', aliases=('manual', '帮助', '说明', '使用说明', '幫助', '說明', '使用說明'), only_to_me=False)
async def send_help(session:CommandSession):
    msg='''
=====================
- HoshinoBot使用说明 -
=====================
输入方括号[]内的关键词即可触发相应的功能
※注意其中的【空格】不可省略！
※部分功能必须手动at本bot才会触发(复制无效)
※本bot的功能采取模块化管理，群管理可控制开关
※※调教时请注意使用频率，您的滥用可能会导致bot帐号被封禁
===从此开始↓一行距===

==================
- 公主连接Re:Dive -
==================
[@bot来发十连] 十连转蛋模拟(手动at 复制无效)
[@bot来发单抽] 单抽转蛋模拟(手动at 复制无效)
[查看卡池] 查看bot现在的卡池及出率
[怎么拆 妹弓] 后以空格隔开接角色名，查询竞技场解法
[pcr速查] 常用网址/速查表
[bcr速查] B服萌新攻略
[rank表] 查看rank推荐表
[黄骑充电表] 查询黄骑1动充电规律
[@bot官漫132] 官方四格阅览
[禁用 pcr-twitter] 禁用日服官推转发
[启用 pcr-arena-reminder-jp] 背刺时间提醒(UTC+9)
[启用 pcr-arena-reminder-tw] 背刺时间提醒(UTC+8)
[!帮助] 查看会战管理功能的说明
===========
- 通用功能 -
===========
[启用 bangumi] 开启番剧更新推送
- [@bot来点新番] 查看最近的更新(↑需先开启番剧更新推送↑)
[.r] 掷骰子
[.r 3d12] 掷3次12面骰子
[@bot精致睡眠] 8小时精致睡眠(bot需具有群管理权限)
[给我来一份精致昏睡下午茶套餐] 叫一杯先辈特调红茶(bot需具有群管理权限)
[@bot来杯咖啡] 联系维护组，空格后接反馈内容
==========
- 艦これ -
==========
[启用 hourcall] 时报
[启用 kc-reminder] 演习/月常远征提醒
[启用 kc-twitter] 官推转发
[启用 kc-query] 开启kancolle查询功能(下详)
- [*晓改二] 舰娘信息查询
- [*震电] 装备信息查询
- [人事表200102] 查询战果人事表(年/月/服务器)
[.qj 晓] 预测ケッコンカッコカリ运值增加（准确率高达25%）
=================
- 群管理限定功能 -
=================
[翻译 もう一度、キミとつながる物語] 机器翻译
[lssv] 查看功能模块的开关状态

========
※除帮助中写明外 另有其他隐藏功能:)
※服务器运行需要成本，赞助支持请私戳作者
※本bot开源，可自行搭建
※您的支持是本bot更新维护的动力

※※初次使用请仔细阅读帮助开头的注意事项
※※调教时请注意使用频率，您的滥用可能会导致bot帐号被封禁
'''.strip()
    await session.send(msg)

_last_coffee_day = -1
_user_coffee_count = defaultdict(int)    # {user: gacha_count}
_max_coffee_per_day = 1
COFFEE_EXCEED_NOTICE = f'您今天已经喝过{_max_coffee_per_day}杯了，请明天再来！'

def check_coffee_num(user_id):
    global _last_coffee_day, _user_coffee_count, _max_coffee_per_day
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    day = (now - timedelta(hours=5)).day
    if day != _last_coffee_day:
        _last_coffee_day = day
        _user_coffee_count.clear()
    return bool(_user_coffee_count[user_id] < _max_coffee_per_day)


@on_command('来杯咖啡', permission=perm.GROUP)
async def call_master(session:CommandSession):
    uid = session.ctx['user_id']
    if not check_coffee_num(uid):
        await session.send(COFFEE_EXCEED_NOTICE, at_sender=True)
        return
    _user_coffee_count[uid] += 1

    coffee = session.bot.config.SUPERUSERS[0]
    text = session.current_arg
    if not text:
        await session.send(MessageSegment.at(coffee))
    else:
        await session.bot.send_private_msg(self_id=session.ctx['self_id'], user_id=coffee, message=f'Q{uid}@群{session.ctx["group_id"]}\n{text}')
        await session.send(f'您的反馈已发送！\n=======\n{text}', at_sender=True)
