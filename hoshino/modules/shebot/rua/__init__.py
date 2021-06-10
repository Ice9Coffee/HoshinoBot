import re
from io import BytesIO
from os import path

from PIL import Image

from hoshino import Service, aiorequests, priv
from hoshino.typing import HoshinoBot, CQEvent
from .data_source import generate_gif
from .._res import Res as R

sv_help = '''
[@人 rua]
'''.strip()

sv = Service(
    name='Rua',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 是否可见
    enable_on_default=True,  # 是否默认启用
    bundle='娱乐',  # 属于哪一类
    help_=sv_help  # 帮助文本
)

data_dir = path.join(path.dirname(__file__), 'data')


@sv.on_message()
async def creep(bot: HoshinoBot, ev: CQEvent):
    match = re.match(r'(?:(?:rua)|(?:Rua)|搓)\[CQ:at,qq=(\d+?)\]', ev.raw_message)
    if not match:
        match = re.match(r'\[CQ:at,qq=(.+?)\] (?:(?:rua)|(?:Rua)|搓)', ev.raw_message)
    if not match:
        return
    creep_id = match.group(1)

    url = f'http://q1.qlogo.cn/g?b=qq&nk={creep_id}&s=160'
    resp = await aiorequests.get(url)
    resp_cont = await resp.content
    avatar = Image.open(BytesIO(resp_cont))
    output = generate_gif(data_dir, avatar)
    print(output)
    await bot.send(ev, R.image(output))
