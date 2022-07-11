from hoshino.service import Service
from hoshino import R

sv_help = '''
[人事表200102] 战果人事表(数字为 年/月/服务器)
[.qj 晓] 预测运值增加(准确率高达25%)(需开启dice)
[1-1] 直达梦美妈妈攻略贴
[*晓改二] 舰娘信息查询(暂不可用)
[*震电] 装备信息查询(暂不可用)
=== 速查表 ===
[dd2][远征][蜜瓜][抗击坠]
'''.strip()
sv = Service('kc-query', enable_on_default=False, help_=sv_help, bundle='kancolle')

# sv.on_fullmatch('拆包')(lambda bot, ev: bot.send(ev, 'bbs.nga.cn/read.php?tid=28148427'))
# temp = '''极简信息搬运贴bbs.nga.cn/read.php?tid=28130801
# 与Верный酱的地中海假日bbs.nga.cn/read.php?tid=28149658
# 记者的舰娘笔记bbs.nga.cn/read.php?tid=28154058
# 目白麦昆开荒组bbs.nga.cn/read.php?tid=28142296
# 地中海就是波罗的海，马耳他就是奥兰bbs.nga.cn/read.php?tid=28142877
# ぜかましzekamashi.net/category/202108-event/
# '''
# sv.on_fullmatch('e1攻略', 'E1攻略')(lambda bot, ev: bot.send(ev, temp))
# sv.on_fullmatch('e2攻略', 'E2攻略')(lambda bot, ev: bot.send(ev, temp))
# sv.on_fullmatch('e3攻略', 'E3攻略')(lambda bot, ev: bot.send(ev, temp))
# sv.on_fullmatch('e4攻略', 'E4攻略')(lambda bot, ev: bot.send(ev, temp))
# sv.on_fullmatch('e5攻略', 'E5攻略')(lambda bot, ev: bot.send(ev, temp))

sv.on_fullmatch('驱逐改二', 'dd改二', 'DD改二', 'dd2')(lambda bot, ev: bot.send(ev, R.img('kancolle/quick/驱逐改二早见表.jpg').cqcode + R.img('kancolle/quick/驱逐改早见表.jpg').cqcode))
sv.on_fullmatch('远征')(lambda bot, ev: bot.send(ev, f"bbs.nga.cn/read.php?tid=21866416 {R.img('kancolle/quick/远征大成功.png').cqcode} {R.img('kancolle/quick/远征大成功简.png').cqcode}"))
sv.on_fullmatch('蜜瓜', '夕张')(lambda bot, ev: bot.send(ev, f"https://zh.kcwiki.cn/wiki/%E5%A4%95%E5%BC%A0#.E6.88.98.E6.96.97.E7.89.B9.E6.80.A7 {R.img('kancolle/quick/夕张改二装备适性.png').cqcode}"))
sv.on_fullmatch('对空回避', '抗击坠', '抗击坠表')(lambda bot, ev: bot.send(ev, f"https://docs.google.com/spreadsheets/d/1cfV8sHvX1vMEQcckQaG1cBCXWctnS0P_GT9z74EotPw {R.img('kancolle/quick/对空回避.png').cqcode}"))

# ==================================== #

sv.on_fullmatch('日常', '周常', '月常', '季常', '年常')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454450573"))

sv.on_fullmatch('1-1')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454451942"))
sv.on_fullmatch('1-2')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454452006"))
sv.on_fullmatch('1-3')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454452053"))
sv.on_fullmatch('1-4')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454452119"))
sv.on_fullmatch('1-5')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454452178"))
sv.on_fullmatch('1-6')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454452236"))

sv.on_fullmatch('2-1')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454452562"))
sv.on_fullmatch('2-2')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454452628"))
sv.on_fullmatch('2-3')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454452698"))
sv.on_fullmatch('2-4')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454452788"))
sv.on_fullmatch('2-5')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454452843"))

sv.on_fullmatch('3-1')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454453286"))
sv.on_fullmatch('3-2')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454453344"))
sv.on_fullmatch('3-3')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454453396"))
sv.on_fullmatch('3-4')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454453451"))
sv.on_fullmatch('3-5')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454453495"))

sv.on_fullmatch('7-1')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454455961"))
sv.on_fullmatch('7-2')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454456055"))
sv.on_fullmatch('7-3')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454456110"))
sv.on_fullmatch('7-4')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454456265"))

sv.on_fullmatch('4-1')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454453876"))
sv.on_fullmatch('4-2')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454454019"))
sv.on_fullmatch('4-3')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454454084"))
sv.on_fullmatch('4-4')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454454163"))
sv.on_fullmatch('4-5')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454454205"))

sv.on_fullmatch('5-1')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454454625"))
sv.on_fullmatch('5-2')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454454730"))
sv.on_fullmatch('5-3')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454454783"))
sv.on_fullmatch('5-4')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454454829"))
sv.on_fullmatch('5-5')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454454888"))

sv.on_fullmatch('6-1')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454455307"))
sv.on_fullmatch('6-2')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454455364"))
sv.on_fullmatch('6-3')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454455426"))
sv.on_fullmatch('6-4')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454455513"))
sv.on_fullmatch('6-5')(lambda bot, ev: bot.send(ev, "https://bbs.nga.cn/read.php?pid=454455575"))



from .fleet import *
from .senka import *
