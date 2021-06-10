import requests, random, os, json
from hoshino import Service, R, priv
from hoshino.typing import CQEvent
from hoshino.util import DailyNumberLimiter
import hoshino

sv_help = '''
[今天吃啥/今天吃什么/吃点啥/吃啥] 看看今天吃啥
'''.strip()

sv = Service(
    name='今天吃啥',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.ADMIN,  # 管理权限
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    bundle='娱乐',  # 分组归类
    help_=sv_help  # 帮助说明
)

_day_limit = 3
_lmt = DailyNumberLimiter(_day_limit)
absPath = './hoshino/modules/what_to_eat/'


def get_foods():
    if os.path.exists(absPath + 'foods.json'):
        with open(absPath + 'foods.json', "r", encoding='utf-8') as dump_f:
            try:
                words = json.load(dump_f)
            except Exception as e:
                hoshino.logger.error(f'读取食谱时发生错误{type(e)}')
                return None
    else:
        hoshino.logger.error(f'目录下未找到食谱')
    keys = list(words.keys())
    key = random.choice(keys)

    return words[key]["name"]


@sv.on_rex(r'^(今天|早上|中午|晚上|夜宵)吃(什么|啥|点啥)')
async def net_ease_cloud_word(bot, ev: CQEvent):
    uid = ev.user_id
    if not _lmt.check(uid):
        return
    _lmt.increase(uid)
    food_name = get_foods()
    to_eat = f'今天去吃{food_name}吧~'
    try:
        to_eat += '\n' + R.img(f'foods/{food_name}.jpg').cqcode
    except Exception as e:
        hoshino.logger.error(f'读取食物图片时发生错误{type(e)}')
    await bot.send(ev, to_eat)
