import datetime
import random
import string
import aiohttp
import asyncio
import traceback
import sys
import io
import base64
import json
import os
from hoshino import R
from PIL import Image
from .config import get_config
from hoshino import config

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

ranking_list = {}

ranking_date = None

acggov_headers = {
    'token': config.ACG_GOV_API,
    'referer': 'https://www.acgmx.com/'
}

native_info = {}


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


def generate_image_struct():
    return {
        'id': 0,
        'url': '',
        'title': '',
        'author': '',
        'tags': [],
        'data': None,
        'native': False,
    }


# 读取排行榜
async def query_ranking(date: str, page: int) -> dict:
    if date not in ranking_list:
        ranking_list[date] = {}
    if page in ranking_list[date]:
        return ranking_list[date][page]
    url = f'https://api.acgmx.com/public/ranking'
    params = {
        'ranking_type': 'illust',
        'mode': get_config('acggov', 'ranking_mode'),
        'date': date,
        'per_page': get_config('acggov', 'per_page'),
        'page': page + 1,
    }
    data = {}
    try:
        async with aiohttp.ClientSession(headers=acggov_headers) as session:
            async with session.get(url, params=params, proxy=get_config('acggov', 'acggov_proxy')) as resp:
                data = await resp.json(content_type='application/json')
                ranking_list[date][page] = data
    except:
        traceback.print_exc()
    return data


# 获取随机色图
async def query_setu():
    data = {}
    image = generate_image_struct()
    try:
        async with aiohttp.ClientSession(headers=acggov_headers) as session:
            async with session.get('https://api.acgmx.com/public/setu',
                                   proxy=get_config('acggov', 'acggov_proxy')) as resp:
                data = await resp.json(content_type='application/json')
    except Exception:
        traceback.print_exc()
        image['title'] = '无法访问api'
        return image
    if 'data' not in data:
        image['title'] = 'api返回数据无效'
        return image
    data = data['data']

    image['id'] = data['illust']
    image['title'] = data['title']
    image['author'] = data['user']['name']
    for tag in data['tags']:
        image['tags'].append(tag['name'])
    if get_config('acggov', 'use_thumb'):
        image['url'] = data['large']
    else:
        num = random.randint(0, int(data['pageCount']) - 1)
        image['url'] = data['originals'][num]['url']
    return image


# 获取搜索结果
async def query_search(keyword):
    data = {}
    image_list = []
    image = generate_image_struct()
    url = f'https://api.acgmx.com/public/search'
    params = {
        'q': keyword,
        'offset': 0,
    }
    try:
        async with aiohttp.ClientSession(headers=acggov_headers) as session:
            async with session.get(url, params=params, proxy=get_config('acggov', 'acggov_proxy')) as resp:
                data = await resp.json(content_type='application/json')
    except Exception:
        traceback.print_exc()
        image['title'] = '无法访问api'
        return image_list
    if 'illusts' not in data:
        image['title'] = 'api返回数据无效'
        return image_list

    for item in data['illusts']:
        image = generate_image_struct()
        image['id'] = item['id']
        image['title'] = item['title']
        image['author'] = item['user']['name']
        for tag in item['tags']:
            image['tags'].append(tag['name'])
        try:
            if get_config('acggov', 'use_thumb'):
                image['url'] = item['image_urls']['large']
            else:
                if item['page_count'] == 1:
                    image['url'] = item['meta_single_page']['original_image_url']
                else:
                    num = random.randint(0, item['page_count'] - 1)
                    image['url'] = item['meta_pages'][num]['image_urls']['original']
        except:
            pass
        if image['url']:
            image_list.append(image)
    print('搜索结果数量', len(data['illusts']))
    return image_list


# 获取排行榜图片
async def query_ranking_setu(number: int) -> (int, str):
    image = generate_image_struct()

    page = number // get_config('acggov', 'per_page')
    number = number % get_config('acggov', 'per_page')
    date = (datetime.datetime.now() + datetime.timedelta(days=-2)).strftime("%Y-%m-%d")
    data = await query_ranking(date, page)
    if not 'response' in data:
        image['title'] = '排行榜数据获取失败'
        return image

    illust = data['response'][0]['works'][number]['work']['id']
    image['title'] = data['response'][0]['works'][number]['work']['title']
    image['author'] = data['response'][0]['works'][number]['work']['user']['name']
    for tag in data['response'][0]['works'][number]['work']['tags']:
        image['tags'].append(tag)

    if get_config('acggov', 'use_thumb'):
        image['url'] = data['response'][0]['works'][number]['work']['image_urls']['large']
    else:
        data = {}
        url = 'https://api.acgmx.com/illusts/detail'
        params = {
            'illustId': illust,
            'reduction': 'true',
        }
        try:
            async with aiohttp.ClientSession(headers=acggov_headers) as session:
                async with session.get(url, params=params, proxy=get_config('acggov', 'acggov_proxy')) as resp:
                    data = await resp.json(content_type='application/json')
        except Exception as _:
            traceback.print_exc()
            image['title'] = 'detail获取失败'
            return image
        if 'data' not in data:
            image['title'] = 'detail数据异常'
            return image
        data = data['data']
        page_count = data['illust']['page_count']
        if page_count == 1:
            image['url'] = data['illust']['meta_single_page']['original_image_url']
        else:
            meta_pages = data['illust']['meta_pages']
            num = random.randint(0, len(meta_pages) - 1)
            image['url'] = meta_pages[num]['image_urls']['original']

    image['id'] = illust
    return image


async def download_acggov_image(url: str):
    print('acggov downloading image', url)
    try:
        async with aiohttp.ClientSession(headers=acggov_headers) as session:
            async with session.get(url, proxy=get_config('acggov', 'acggov_proxy')) as resp:
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
    print('acggov downloading pixiv image', url)
    headers = {
        'referer': f'https://www.pixiv.net/member_illust.php?mode=medium&illust_id={id}'
    }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, proxy=get_config('acggov', 'pixiv_proxy')) as resp:
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


def save_image(image, mode='acggov'):
    path = f'setu_mix/{mode}/{image["id"]}'

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


async def get_setu_online():
    image = await query_setu()
    # 检查本地是否存在该图片
    path = f'setu_mix/acggov/{image["id"]}.jpg'
    res = R.img(path)
    if os.path.exists(res.path):
        with open(res.path, 'rb') as f:
            image['data'] = f.read()
            image['native'] = True
    else:
        image['data'] = await download_acggov_image(image['url'])
        image['native'] = False
        if not image['data']:
            image['id'] = 0
            image['title'] = '图片下载失败'
            return image
        if get_config('acggov', 'mode') == 2:
            save_image(image)
    return image


def get_setu_native(uid=0):
    image = generate_image_struct()

    path = f'setu_mix/acggov'
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

    path = f'setu_mix/acggov/{uid}'
    res = R.img(path)
    try:
        with open(res.path + '.jpg', 'rb') as f:
            image['data'] = f.read()
        with open(res.path + '.json', encoding='utf8') as f:
            d = json.load(f)
            for k, v in d.items():
                image[k] = v
    except:
        pass

    return image


async def search_setu_online(keyword, num):
    image_list = await query_search(keyword)
    valid_list = []
    while len(image_list) > 0:
        image = image_list.pop(random.randint(0, len(image_list) - 1))
        # 检查本地是否存在该图片
        path = f'setu_mix/acggov/{image["id"]}.jpg'
        res = R.img(path)
        if os.path.exists(res.path):
            with open(res.path, 'rb') as f:
                image['data'] = f.read()
                image['native'] = True
        else:
            url = image['url']
            if get_config('acggov', 'pixiv_direct'):
                image['data'] = await download_pixiv_image(url, image['id'])
            else:
                url = url.replace("https://i.pximg.net", "https://i.pixiv.cat")
                image['data'] = await download_acggov_image(url)
            image['native'] = False
            if image['data']:
                if get_config('acggov', 'mode') == 2:
                    save_image(image)
        if image['data']:
            valid_list.append(image)
        if len(valid_list) >= num:
            break
    return valid_list


def search_setu_native(keyword, num):
    image = generate_image_struct()
    result_list = []
    for k, v in native_info.items():
        if v.find(keyword) >= 0:
            result_list.append(k)

    if len(result_list) > num:
        result_list = random.sample(result_list, num)
    image_list = []
    for result in result_list:
        image = get_setu_native(result)
        if image['data']:
            image_list.append(image)
    return image_list


async def acggov_get_setu():
    if get_config('acggov', 'mode') >= 2:
        return get_setu_native()
    elif get_config('acggov', 'mode') == 1:
        return await get_setu_online()
    else:
        return None


async def acggov_search_setu(keyword, num):
    if get_config('acggov', 'mode') == 1 or get_config('acggov', 'mode') == 2:
        return await search_setu_online(keyword, num)
    elif get_config('acggov', 'mode') == 3:
        return search_setu_native(keyword, num)
    else:
        return None


# 获取排行榜
async def acggov_get_ranking(page: int = 0) -> (int, str):
    date = (datetime.datetime.now() + datetime.timedelta(days=-2)).strftime("%Y-%m-%d")
    data = await query_ranking(date, page)
    if not 'response' in data:
        return '数据获取失败'
    works = data['response'][0]['works']
    pages = data['pagination']['pages']
    current = data['pagination']['current']
    num = page * get_config('acggov', 'per_page') + 1
    msg = ''
    for i in works:
        msg += f'{num}.' + i['work']['title'] + '-' + str(i['work']['id']) + '\n'
        num += 1
    msg += f'第{current}页，共{str(pages)}页'
    return msg


# 获取排行榜图片
async def acggov_get_ranking_setu(number: int) -> (int, str):
    image = await query_ranking_setu(number)

    path = f'setu_mix/acggov/{image["id"]}.jpg'
    res = R.img(path)
    if os.path.exists(res.path):
        with open(res.path, 'rb') as f:
            image['data'] = f.read()
            image['native'] = True
    else:
        url = image['url']
        if get_config('acggov', 'pixiv_direct'):
            image['data'] = await download_pixiv_image(url, image['id'])
        else:
            url = url.replace("https://i.pximg.net", "https://i.pixiv.cat")
            image['data'] = await download_acggov_image(url)
        image['native'] = False
        if not image['data']:
            image['id'] = 0
            image['title'] = '图片下载失败'
        elif get_config('acggov', 'mode') == 2:
            save_image(image)

    return image


async def acggov_fetch_process():
    global ranking_date
    if get_config('acggov', 'mode') == 2:
        print('fetch acggov setu')
        for _ in range(10):
            await get_setu_online()

        date = (datetime.datetime.now() + datetime.timedelta(days=-2)).strftime("%Y-%m-%d")
        if date != ranking_date:
            print('fetch acggov ranking setu')
            for i in range(25):
                await acggov_get_ranking_setu(i)
            ranking_date = date


def acggov_init():
    global native_info
    if get_config('acggov', 'mode') == 3:
        native_info = load_native_info('acggov')
