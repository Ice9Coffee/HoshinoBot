import os
import json
import traceback
import aiohttp
import io
import random
import datetime
from PIL import Image
from hoshino import R, config
from .config import get_config

quota_limit_time = datetime.datetime.now()


def generate_image_struct():
    return {
        'id': 0,
        'url': '',
        'title': '',
        'author': '',
        'tags': [],
        'r18': False,
        'data': None,
        'native': False,
    }


native_info = {}
native_r18_info = {}


def load_native_info(sub_dir):
    info = {}
    path = f'setu_mix/' + sub_dir
    res = R.img(path)
    if not os.path.exists(res.path):
        return info
    fnlist = os.listdir(res.path)

    for fn in fnlist:
        s = fn.split('.')
        if len(s) != 2 or s[1] != 'json' or not s[0].isdigit():
            continue
        uid = int(s[0])
        try:
            with open(res.path + '/' + fn, encoding='utf8') as f:
                d = json.load(f)
                d['tags'].append(d['title'])
                d['tags'].append(d['author'])
                info[uid] = ','.join(d['tags'])
        except:
            pass
    print('read', len(info), 'setu from', sub_dir)
    return info


# 获取随机色图
async def query_setu(r18=0, keyword=None):
    global quota_limit_time
    image_list = []
    if datetime.datetime.now() < quota_limit_time:
        return image_list

    data = {}
    url = 'https://api.lolicon.app/setu'
    params = {
        'apikey': config.lolicon_api,
        'r18': r18,
        'num': 10,
    }
    if keyword:
        params['keyword'] = keyword
    if get_config('lolicon', 'use_thumb'):
        params['size1200'] = 'true'
    if get_config('lolicon', 'pixiv_direct'):
        params['proxy'] = 'disable'

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json(content_type='application/json')
    except Exception:
        traceback.print_exc()
        return image_list
    if 'code' not in data:
        return image_list
    if data['code'] != 0:
        print('lolicon api error code:', data['code'], ',msg:', data['msg'])
        if data['code'] == 429:
            print('lolicon api 已到达本日调用额度上限')
            quota_limit_time = datetime.datetime.now() + datetime.timedelta(seconds=data['quota_min_ttl'])
        return image_list
    for item in data['data']:
        image = generate_image_struct()
        image['id'] = item['pid']
        image['title'] = item['title']
        image['url'] = item['url']
        image['tags'] = item['tags']
        image['r18'] = item['r18']
        image['author'] = item['author']
        image_list.append(image)
    return image_list


async def download_image(url: str):
    print('lolicon downloading image', url)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.read()
                # 转jpg
                byte_stream = io.BytesIO(data)
                roiImg = Image.open(byte_stream)
                if roiImg.mode != 'RGB':
                    roiImg = roiImg.convert('RGB')
                imgByteArr = io.BytesIO()
                roiImg.save(imgByteArr, format='JPEG')
                return imgByteArr.getvalue()
    except:
        print('download image failed')
        # traceback.print_exc()
    return None


async def download_pixiv_image(url: str, id):
    print('lolicon downloading pixiv image', url)
    headers = {
        'referer': f'https://www.pixiv.net/member_illust.php?mode=medium&illust_id={id}'
    }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, proxy=get_config('lolicon', 'pixiv_proxy')) as resp:
                data = await resp.read()
                # 转jpg
                byte_stream = io.BytesIO(data)
                roiImg = Image.open(byte_stream)
                if roiImg.mode != 'RGB':
                    roiImg = roiImg.convert('RGB')
                imgByteArr = io.BytesIO()
                roiImg.save(imgByteArr, format='JPEG')
                return imgByteArr.getvalue()
    except:
        print('download image failed')
        # traceback.print_exc()
    return None


def save_image(image):
    path = f'setu_mix/lolicon/{image["id"]}'
    if image['r18']:
        path = f'setu_mix/lolicon_r18/{image["id"]}'

    res = R.img(path + '.jpg')
    with open(res.path, 'wb') as f:
        f.write(image['data'])

    res = R.img(path + '.json')
    info = {
        'title': image['title'],
        'author': image['author'],
        'url': image['url'],
        'tags': image['tags'],
    }
    with open(res.path, 'w', encoding='utf8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)


async def get_setu_online(num, r18=0, keyword=None):
    image_list = await query_setu(r18=r18, keyword=keyword)
    valid_list = []

    while len(image_list) > 0:
        image = image_list.pop(random.randint(0, len(image_list) - 1))
        # 检查本地是否存在该图片
        path = f'setu_mix/lolicon/{image["id"]}.jpg'
        if image['r18']:
            path = f'setu_mix/lolicon_r18/{image["id"]}'
        res = R.img(path)
        if os.path.exists(res.path):
            with open(res.path, 'rb') as f:
                image['data'] = f.read()
                image['native'] = True
        else:
            if get_config('lolicon', 'pixiv_direct'):
                image['data'] = await download_pixiv_image(image['url'], image['id'])
            else:
                image['data'] = await download_image(image['url'])
            image['native'] = False
            if image['data'] and get_config('lolicon', 'mode') == 2:
                save_image(image)
        if image['data']:
            valid_list.append(image)
        if len(valid_list) >= num:
            break
    return valid_list


def get_setu_native(r18=0, uid=0):
    image = generate_image_struct()

    path = f'setu_mix/lolicon'
    if r18 == 1:
        path = f'setu_mix/lolicon_r18'
    elif r18 == 2:
        if random.randint(1, 100) > 50:
            path = f'setu_mix/lolicon_r18'
    res = R.img(path)
    if not os.path.exists(res.path):
        return image

    if uid == 0:
        fn = random.choice(os.listdir(res.path))
        if fn.split('.')[0].isdigit():
            uid = int(fn.split('.')[0])

    if not uid:
        return image

    image['id'] = int(uid)
    image['native'] = True

    path += f'/{uid}'
    res = R.img(path)
    try:
        with open(res.path + '.jpg', 'rb') as f:
            image['data'] = f.read()
        with open(res.path + '.json', encoding='utf8') as f:
            d = json.load(f)
            if 'title' in d:
                image['title'] = d['title']
            if 'author' in d:
                image['author'] = d['author']
    except:
        pass

    return image


def search_setu_native(keyword, r18, num):
    result_list = []
    if r18 == 0 or r18 == 2:
        for k, v in native_info.items():
            if v.find(keyword) >= 0:
                result_list.append({
                    'uid': k,
                    'r18': 0,
                })
    if r18 == 1 or r18 == 2:
        for k, v in native_r18_info.items():
            if v.find(keyword) >= 0:
                result_list.append({
                    'uid': k,
                    'r18': 1,
                })
    if len(result_list) > num:
        result_list = random.sample(result_list, num)
    image_list = []
    for result in result_list:
        image = get_setu_native(result['r18'], result['uid'])
        if image['data']:
            image_list.append(image)
    return image_list


# r18: 0 正常 1 r18 2 混合
async def lolicon_get_setu(r18):
    if get_config('lolicon', 'mode') >= 2:
        return get_setu_native(r18)
    elif get_config('lolicon', 'mode') == 1:
        image_list = await get_setu_online(1, r18)
        if len(image_list) > 0:
            return image_list[0]
        else:
            return None
    else:
        return None


# r18: 0 正常 1 r18 2 混合
async def lolicon_search_setu(keyword, r18, num):
    if get_config('lolicon', 'mode') == 1 or get_config('lolicon', 'mode') == 2:
        return await get_setu_online(num, r18, keyword)
    elif get_config('lolicon', 'mode') == 3:  # 离线模式
        return search_setu_native(keyword, r18, num)
    else:
        return None


async def lolicon_fetch_process():
    if get_config('lolicon', 'mode') == 2:
        print('fetch lolicon setu')
        await get_setu_online(10, 0)
        if get_config('lolicon', 'r18'):
            print('fetch lolicon r18 setu')
            await get_setu_online(10, 1)


def lolicon_init():
    global native_info
    global native_r18_info
    if get_config('lolicon', 'mode') == 3:
        native_info = load_native_info('lolicon')
        native_r18_info = load_native_info('lolicon_r18')


'''
class Lolicon:

    def __init__(self):
        pass

    async def get_setu(self):
        pass

    async def search_setu(self):
        pass

    async def get_ranking(self):
        pass

    async def get_ranking_setu(self):
        pass

    async def fetch_process(self):
        await lolicon_fetch_process()
'''
