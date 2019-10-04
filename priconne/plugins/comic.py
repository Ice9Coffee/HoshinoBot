import re
import json
import requests
from urllib.parse import urljoin
from os import path
from nonebot import CommandSession, on_command

from .util import get_cqimg, silence

def get_img_bed():
    config_file = path.join(path.dirname(__file__), "config.json")
    with open(config_file) as f:
        config = json.load(f)
        return config["IMG_BED"]


def load_index():
    base = get_img_bed()
    url = urljoin(base, './priconne/comic/index.json')
    resp = requests.get(url)
    return resp.json()


def get_pic_name(id_):
    pre = 'episode_'
    end = '.png'
    return f'{pre}{id_}{end}'


@on_command('官漫')
async def comic(session:CommandSession):
    rex = re.compile(r'\d{1,3}')
    arg = session.current_arg_text.strip()
    
    if not rex.match(arg):
        await session.finish('请输入漫画集数 如：官漫 132')
        return
    episode = str(int(arg))
    index = load_index()
    if episode not in index:
        await session.finish(f'未查找到第{episode}话，敬请期待官方更新')
        return
    title = index[episode]['title']
    pic = get_cqimg(get_pic_name(episode), './priconne/comic/', get_img_bed())
    msg = f'プリンセスコネクト！Re:Dive公式4コマ\n第{episode}話 {title}\n{pic}'
    await session.send(msg)
    await silence(session, 1*60)

