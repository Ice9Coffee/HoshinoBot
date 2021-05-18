from hoshino.service import Service

sv_help = '''
[*晓改二] 舰娘信息查询
[*震电] 装备信息查询
[人事表200102] 战果人事表(年/月/服务器)
[.qj 晓] 预测运值增加（准确率高达25%）（需开启dice）
'''.strip()
sv = Service('kc-query', enable_on_default=False, help_=sv_help, bundle='kancolle')

sv.on_fullmatch(('e1攻略', 'E1攻略'))(lambda bot, ev: bot.send(ev, 'bbs.nga.cn/read.php?pid=514129578'))
sv.on_fullmatch(('e2攻略', 'E2攻略'))(lambda bot, ev: bot.send(ev, 'bbs.nga.cn/read.php?pid=514129640'))
sv.on_fullmatch(('e3攻略', 'E3攻略'))(lambda bot, ev: bot.send(ev, 'bbs.nga.cn/read.php?pid=514129692'))
sv.on_fullmatch(('e4攻略', 'E4攻略'))(lambda bot, ev: bot.send(ev, 'bbs.nga.cn/read.php?pid=514129759'))
sv.on_fullmatch(('e5攻略', 'E5攻略'))(lambda bot, ev: bot.send(ev, 'bbs.nga.cn/read.php?pid=514129810'))

from .fleet import *
from .senka import *
