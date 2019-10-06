import re
import json
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs
from os import path

import nonebot
from nonebot import CommandSession, on_command, CQHttpError

from .util import get_cqimg, silence


def get_config():
    config_file = path.join(path.dirname(__file__), "config.json")
    with open(config_file) as f:
        config = json.load(f)
        return config


def get_img_bed():
    return get_config()["IMG_BED"]


def get_subscribe_group():
    return get_config()["SUBSCRIBE_GROUP"]



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
    await silence(session, 1*60)
    await session.send(msg)


def download_comic(id_):
    '''
    下载指定id的官方四格漫画，同时更新漫画目录index.json
    episode_num可能会小于id
    '''
    base = 'https://comic.priconne-redive.jp/api/detail/'
    save_dir = '/home/wad/mywebsite/static/img/priconne/comic/'
    index = load_index()

    def get_pic_name(id_):
        pre = 'episode_'
        end = '.png'
        return f'{pre}{id_}{end}'

    def download_img(save_path, link):
        '''
        从link下载图片保存至save_path（目录+文件名）
        会覆盖原有文件，需保证目录存在
        '''
        print('download_img from ', link, end=' ')
        resp = requests.get(link, stream=True)
        print('status_code=', resp.status_code, end=' ')
        if 200 == resp.status_code:
            if re.search(r'image', resp.headers['content-type'], re.I):
                print(f'is image, saving to {save_path}', end=' ')
                with open(save_path, 'wb') as f:
                    f.write(resp.content)
                    print('ok', end=' ')


    # 先从api获取detail，其中包含图片真正的链接
    print('getting comic', id_, '...', end=' ')
    url = base + id_
    print('url=', url, end=' ')
    resp = requests.get(url)
    print('status_code=', resp.status_code)
    if 200 != resp.status_code:
        return
    data = resp.json()[0]

    episode = data['episode_num']
    title = data['title']
    link = data['cartoon']
    index[episode] = {'title': title, 'link': link}
    print(index[episode])

    # 下载图片并保存
    download_img(path.join(save_dir, get_pic_name(episode)), link)
    print('\n', end='')

    # 保存官漫目录信息
    with open(path.join(save_dir, 'index.json'), 'w', encoding='utf8') as f:
        json.dump(index, f, ensure_ascii=False)


@nonebot.scheduler.scheduled_job('cron', minute='*/5', second='25', jitter=4)
async def update_seeker():
    '''
    轮询官方四格漫画更新
    若有更新则推送至订阅群
    '''
    index_api = 'https://comic.priconne-redive.jp/api/index'
    index = load_index()

    # try:
    # 获取最新漫画信息
    resp = requests.get(index_api, timeout=10)
    data = resp.json()
    id_ = data['latest_cartoon']['id']
    episode = data['latest_cartoon']['episode_num']
    title = data['latest_cartoon']['title']

    # 检查是否已在目录中
    # 同一episode可能会被更新为另一张图片（官方修正），此时episode不变而id改变
    # 所以需要两步判断
    if episode in index:
        qs = urlparse(index[episode]['link']).query
        old_id = parse_qs(qs)['id'][0]
        if id_ == old_id:
            print(f'[{datetime.now()}] 未检测到官漫更新')
            return
    
    # 确定已有更新，下载图片
    print(f'[{datetime.now()}] 发现更新 id=', id_)
    download_comic(id_)

    # 推送至各个订阅群
    pic = get_cqimg(get_pic_name(episode), './priconne/comic/', get_img_bed())
    msg = f'プリンセスコネクト！Re:Dive公式4コマ更新！\n第{episode}話 {title}\n{pic}'

    bot = nonebot.get_bot()
    for group in get_subscribe_group():
        try:
            await bot.send_group_msg(group_id=group, message=msg)
            print(f'群{group} 投递成功')
        except CQHttpError as e:
            print(e)
            print(f'Error：群{group} 投递失败')


    # except Exception as e:
    #     print(f'[{datetime.now()}] update_seeker Error: {e}')

    print(f'[{datetime.now()} 计划任务：update_seeker] 完成')
