from hoshino.service import Service

sv_help = '''
[*晓改二] 舰娘信息查询
[*震电] 装备信息查询
[人事表200102] 战果人事表(年/月/服务器)
[.qj 晓] 预测运值增加（准确率高达25%）（需开启dice）
'''.strip()
sv = Service('kc-query', enable_on_default=False, help_=sv_help, bundle='kancolle')

from .fleet import *
from .senka import *
