from hoshino.service import Service
from hoshino import R
from hoshino.util import FreqLimiter
from hoshino.typing import CQEvent

sv_help = '''
[人事表200102] 战果人事表(数字为 年/月/服务器)
[.qj 晓] 预测运值增加(准确率高达25%)(需开启dice)
[1-1] 直达梦美妈妈攻略贴
[*晓改二] 舰娘信息查询(暂不可用)
[*震电] 装备信息查询(暂不可用)
=== 速查表 ===
[dd2][远征][蜜瓜][抗击坠][攻略]
'''.strip()
sv = Service('kc-query', enable_on_default=False, help_=sv_help, bundle='kancolle')


limiter = FreqLimiter(120)

@sv.on_fullmatch('攻略', 'e1', 'e2', 'e3', 'e4', 'e5', 'E1', 'E2', 'E3', 'E4', 'E5')
async def _(bot, ev: CQEvent):
    if limiter.check(ev.group_id):
        await bot.send(ev, '''
2022夏&初秋活「大規模反攻上陸！トーチ作戦！」
秋月牧场 nga.178.com/read.php?tid=33228729
双子座 nga.178.com/read.php?tid=33238545
十级证书 nga.178.com/read.php?tid=33243768
风岛 zekamashi.net/202208-event/torch-sougou/
IceCirno的活动记录 nga.178.com/read.php?tid=33282039
其他关键词：[拆包][带路][信息搬运]
'''.strip())
        limiter.start_cd(ev.group_id)

sv.on_fullmatch('拆包')(lambda bot, ev: bot.send(ev, '2022夏活拆包集中讨论\nhttps://nga.178.com/read.php?tid=33241849'))
sv.on_fullmatch('带路')(lambda bot, ev: bot.send(ev, '极简版[大規模反攻上陸！トーチ作戦！]信息搬运贴\nhttps://nga.178.com/read.php?tid=33242680'))
sv.on_fullmatch('信息搬运')(lambda bot, ev: bot.send(ev, '[大规模反复迷路]2022年夏活海图带路条件\nhttps://nga.178.com/read.php?tid=33233876'))

sv.on_fullmatch('驱逐改二', 'dd改二', 'DD改二', 'dd2')(lambda bot, ev: bot.send(ev, R.img('kancolle/quick/驱逐改二早见表.jpg').cqcode + R.img('kancolle/quick/驱逐改早见表.jpg').cqcode))
sv.on_fullmatch('远征')(lambda bot, ev: bot.send(ev, f"nga.178.com/read.php?tid=21866416 {R.img('kancolle/quick/远征大成功.png').cqcode} {R.img('kancolle/quick/远征大成功简.png').cqcode}"))
sv.on_fullmatch('蜜瓜', '夕张')(lambda bot, ev: bot.send(ev, f"https://zh.kcwiki.cn/wiki/%E5%A4%95%E5%BC%A0#.E6.88.98.E6.96.97.E7.89.B9.E6.80.A7 {R.img('kancolle/quick/夕张改二装备适性.png').cqcode}"))
sv.on_fullmatch('对空回避', '抗击坠', '抗击坠表')(lambda bot, ev: bot.send(ev, f"https://docs.google.com/spreadsheets/d/1cfV8sHvX1vMEQcckQaG1cBCXWctnS0P_GT9z74EotPw {R.img('kancolle/quick/对空回避.png').cqcode}"))

# ==================================== #

sv.on_fullmatch('日常', '周常', '月常', '季常', '年常')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454450573"))

sv.on_fullmatch('1-1')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454451942"))
sv.on_fullmatch('1-2')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454452006"))
sv.on_fullmatch('1-3')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454452053"))
sv.on_fullmatch('1-4')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454452119"))
sv.on_fullmatch('1-5')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454452178"))
sv.on_fullmatch('1-6')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454452236"))

sv.on_fullmatch('2-1')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454452562"))
sv.on_fullmatch('2-2')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454452628"))
sv.on_fullmatch('2-3')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454452698"))
sv.on_fullmatch('2-4')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454452788"))
sv.on_fullmatch('2-5')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454452843"))

sv.on_fullmatch('3-1')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454453286"))
sv.on_fullmatch('3-2')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454453344"))
sv.on_fullmatch('3-3')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454453396"))
sv.on_fullmatch('3-4')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454453451"))
sv.on_fullmatch('3-5')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454453495"))

sv.on_fullmatch('7-1')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454455961"))
sv.on_fullmatch('7-2')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454456055"))
sv.on_fullmatch('7-3')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454456110"))
sv.on_fullmatch('7-4')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454456265"))

sv.on_fullmatch('4-1')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454453876"))
sv.on_fullmatch('4-2')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454454019"))
sv.on_fullmatch('4-3')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454454084"))
sv.on_fullmatch('4-4')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454454163"))
sv.on_fullmatch('4-5')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454454205"))

sv.on_fullmatch('5-1')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454454625"))
sv.on_fullmatch('5-2')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454454730"))
sv.on_fullmatch('5-3')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454454783"))
sv.on_fullmatch('5-4')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454454829"))
sv.on_fullmatch('5-5')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454454888"))

sv.on_fullmatch('6-1')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454455307"))
sv.on_fullmatch('6-2')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454455364"))
sv.on_fullmatch('6-3')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454455426"))
sv.on_fullmatch('6-4')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454455513"))
sv.on_fullmatch('6-5')(lambda bot, ev: bot.send(ev, "https://nga.178.com/read.php?pid=454455575"))



from .fleet import *
from .senka import *
