from hoshino.service import Service
from hoshino import R

sv_help = '''
[人事表200102] 战果人事表(数字为 年/月/服务器)
[.qj 晓] 预测运值增加(准确率高达25%)(需开启dice)
[e5攻略] 直达梦美妈妈攻略贴
[*晓改二] 舰娘信息查询(暂不可用)
[*震电] 装备信息查询(暂不可用)
=== 速查表 ===
[dd2][远征][蜜瓜]
'''.strip()
sv = Service('kc-query', enable_on_default=False, help_=sv_help, bundle='kancolle')

sv.on_fullmatch('e1攻略', 'E1攻略')(lambda bot, ev: bot.send(ev, 'bbs.nga.cn/read.php?pid=514129578'))
sv.on_fullmatch('e2攻略', 'E2攻略')(lambda bot, ev: bot.send(ev, 'bbs.nga.cn/read.php?pid=514129640'))
sv.on_fullmatch('e3攻略', 'E3攻略')(lambda bot, ev: bot.send(ev, 'bbs.nga.cn/read.php?pid=514129692'))
sv.on_fullmatch('e4攻略', 'E4攻略')(lambda bot, ev: bot.send(ev, 'bbs.nga.cn/read.php?pid=514129759'))
sv.on_fullmatch('e5攻略', 'E5攻略')(lambda bot, ev: bot.send(ev, 'bbs.nga.cn/read.php?pid=514129810'))

sv.on_fullmatch('驱逐改二', 'dd改二', 'DD改二', 'dd2')(lambda bot, ev: bot.send(ev, R.img('kancolle/quick/驱逐改二早见表.jpg').cqcode))
sv.on_fullmatch('远征')(lambda bot, ev: bot.send(ev, f"bbs.nga.cn/read.php?tid=21866416 {R.img('kancolle/quick/远征大成功.png').cqcode}"))
sv.on_fullmatch('蜜瓜', '夕张')(lambda bot, ev: bot.send(ev, f"https://zh.kcwiki.cn/wiki/%E5%A4%95%E5%BC%A0#.E6.88.98.E6.96.97.E7.89.B9.E6.80.A7 {R.img('kancolle/quick/夕张改二装备适性.png').cqcode}"))


from .fleet import *
from .senka import *
