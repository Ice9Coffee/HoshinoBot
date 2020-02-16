import pytz
from datetime import datetime, timedelta
from collections import defaultdict


from nonebot import on_command, CommandSession, MessageSegment
import nonebot.permission as perm

@on_command('help', aliases=('manual', '帮助', '说明', '使用说明', '幫助', '說明', '使用說明'), only_to_me=False)
async def send_help(session:CommandSession):
    msg='''【帮助】
下面是本bot支持的功能
输入冒号后的文本即可使用
※@bot表明该功能必须at本bot才会触发
※请将说明中的所有+号替换为空格
※开启/关闭功能限群管理操作
===从此开始↓一行距===

公主连接Re:Dive
- 抽卡模拟：@bot来发十连 或 @bot来发单抽
- jjc查询：怎么拆+布丁+饭团+兔子+小仓唯
- 查看bot卡池：看看卡池
- rank推荐表：日服rank表 或 台服rank表
- 常用网址：pcr速查
- プリコネRe:Dive官方四格查阅：@bot官漫123
+ プリコネRe:Dive官方四格推送（默认开启）
- 会战管理（请见github.com/Ice-Cirno/HoshinoBot）

蜜柑番剧
* 启用本模块：开启+bangumi
- 查看最近更新：@bot来点新番
+ 番剧推送（开启本模块后自动启用）

艦これ
+ 演习时间提醒：开启+kc-enshu-reminder
+ 时报：开启+hourcall

通用
- 查看本群启用的功能：服务列表
- 启用功能：启用+service_name
- 禁用功能：禁用+service_name
- 机器翻译（限群管理使用）： 翻译+もう一度、キミとつながる物語
- 联系作者：@bot来杯咖啡+你的反馈内容

※调教时请注意使用频率，您的滥用可能会导致bot帐号被封禁
※除上述之外 另有其他隐藏功能:)
※本bot开源 可免费使用
※赞助支持请直接联系作者，您的支持是本bot更新维护的动力
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
