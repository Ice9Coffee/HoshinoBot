import os
import re
import time
import datetime
import random
import urllib
import urllib.request
import io
from PIL import Image
import hoshino
from hoshino import Service, aiorequests

sv = Service('acggov', enable_on_default=True, help_='ACGGOV涩图')


class AcgGov:

    @staticmethod
    def get_token():
        return hoshino.config.acggov.ACG_GOV_API_KEY

    @staticmethod
    def get_url():
        return hoshino.config.acggov.ACG_GOV_AMAZING_PIC_URL

    @staticmethod
    def get_path():
        return hoshino.config.acggov.ACG_GOV_IMG_PATH

    @staticmethod
    def get_origin():
        return hoshino.config.acggov.ACG_GOV_PIC_ORIGIN

    @staticmethod
    def get_admin():
        return hoshino.config.__bot__.SUPERUSERS

    @staticmethod
    def set_origin(boolean):
        hoshino.config.acggov.ACG_GOV_PIC_ORIGIN = boolean
        return hoshino.config.acggov.ACG_GOV_PIC_ORIGIN


@sv.on_fullmatch({'来点色图', '來点涩图', 'setu', '就这', '我好了'})
async def send_Amazing_Pic(bot, ev):
    try:
        print(ev)
        robotId = ev['self_id']
        userId = ev['user_id']
        headers = {'token': AcgGov.get_token()}
        resp = await aiorequests.get(AcgGov.get_url(), headers=headers, timeout=10, stream=True)
        # 判断调用次数已超标
        if resp.status_code != 200:
            await bot.send(ev, f'[CQ:at,qq={userId}]' + '您的请求频率过快，请一分钟后再试')
            return
        res = await resp.json()
        illust = res['data']['illust']
        pageCount = res['data']['pageCount']
        originals = res['data']['originals']
        suffix = None
        r = None
        img = None

        if AcgGov.get_origin():
            # 略微缩略图
            r = urllib.request.urlopen(res['data']['large'])
            byte_stream = io.BytesIO(r.read())
            roiImg = Image.open(byte_stream)
            imgByteArr = io.BytesIO()
            roiImg.save(imgByteArr, format='JPEG')
            imgByteArr = imgByteArr.getvalue() + bytes("jneth", encoding="utf8")
            # 拼接图片路径
            path = AcgGov.get_path() + "/" + illust + ".jpg"
            with open(path, "wb") as f:
                f.write(imgByteArr)
                print("done")
                del r
            await bot.send(ev, f'[CQ:at,qq={userId}][CQ:image,file={illust + ".jpg"}]')
            os.remove(path)
        else:
            # 高清图
            # 如果只有一页
            if pageCount == 1:
                file = urllib.request.urlopen(originals[0]['url'])
                tmpIm = io.BytesIO(file.read())
                img = Image.open(tmpIm)
                suffix = img.format
                r = await aiorequests.get(originals[0]['url'], stream=True)
            else:
                # 多页随机
                num = random.randint(1, int(pageCount))
                file = urllib.request.urlopen(originals[num - 1]['url'])
                tmpIm = io.BytesIO(file.read())
                img = Image.open(tmpIm)
                suffix = img.format
                r = await aiorequests.get(originals[num - 1]['url'], stream=True)

            # 拼接图片路径
            path = AcgGov.get_path() + "/" + illust + "." + suffix
            # 判断返回HTTP码是否为200
            if r.status_code == 200:
                # 写入本地并修改md5
                open(path, 'wb+').write(await r.content + bytes("jneth", encoding="utf8"))
                print("done")
                del r
                await bot.send(ev, f'[CQ:at,qq={userId}][CQ:image,file={illust + "." + suffix}]')
                os.remove(path)

    except Exception as e:
        sv.logger.error(f'Error: {e}')


@sv.on_fullmatch({'修改涩图模式'})
async def change_type(bot, ev):
    try:
        userId = ev['user_id']
        # 判断是否是超级管理员
        if userId in AcgGov.get_admin():
            # 修改模式，如果是原图修改缩略图，反之亦然
            if AcgGov.get_origin():
                AcgGov.set_origin(False)
            else:
                AcgGov.set_origin(True)

            if AcgGov.get_origin():
                msg = '缩略图'
            else:
                msg = '高清图'

            await bot.send(ev, f'[CQ:at,qq={userId}]修改成功，当前模式为{msg}')
        else:
            # 拼接超级管理员
            message = f'[CQ:at,qq={userId}]您无权限，本命令只有'
            for i in AcgGov.get_admin():
                message += '[CQ:at,qq=' + str(i) + ']'

            await bot.send(ev, message + '可使用')
    except Exception as e:
        sv.logger.error(f'Error: {e}')


# 以下是读取pixiv的中转18x排行榜
@sv.on_prefix("本日涩图排行榜")
async def ranking_r18(bot, ev):
    try:
        robotId = ev['self_id']
        userId = ev['user_id']
        # 每页显示的数量
        per_page = 10
        page = ev['raw_message'].replace("本日涩图排行榜", "").replace(" ", "")
        # 判断是否是数字，不是则给默认值
        if not is_number(page):
            page = 1
        headers = {'token': AcgGov.get_token()}
        nowtime = (datetime.datetime.now() + datetime.timedelta(days=-2)).strftime("%Y-%m-%d")

        resp = await aiorequests.get('https://api.pixiv.hcyacg.com/public/ranking?ranking_type=illust&mode=daily_r18'
                                     '&date=' + nowtime + '&per_page=' + str(per_page) + '&page=' + page,
                                     headers=headers, timeout=10, stream=True)
        # 判断调用次数已超标
        if resp.status_code != 200:
            await bot.send(ev, f'[CQ:at,qq={userId}]' + '您的请求频率过快，请一分钟后再试')
            return
        res = await resp.json()

        data = res['response'][0]['works']
        pages = res['pagination']['pages']
        current = res['pagination']['current']
        num = int(page) * per_page - 9
        message = f'[CQ:at,qq={userId}]' + '\n'
        for i in data:
            message += f'{num}、' + i['work']['title'] + '-' + str(i['work']['id']) + '\n'
            num += 1
        message += f'=======第{current}页，共{str(pages)}页======='

        await bot.send(ev, message)
    except Exception as e:
        sv.logger.error(f'Error: {e}')


# 以下是读取pixiv的中转18x排行榜
@sv.on_prefix("看涩图")
async def look_ranking_r18(bot, ev):
    try:
        robotId = ev['self_id']
        userId = ev['user_id']
        # 每页显示的数量
        per_page = 10
        number = ev['raw_message'].replace("看涩图", "").replace(" ", "")
        # 判断是否是数字，不是则给默认值
        if not is_number(number):
            number = 1

        # 取余
        if int(number) % per_page == 0:
            page = int(number) / per_page
            number = 9
        else:
            page = (int(number) - (int(number) % per_page)) / per_page
            number = int(number) % per_page

        if page == 0:
            page = 1
        headers = {'token': AcgGov.get_token()}
        nowtime = (datetime.datetime.now() + datetime.timedelta(days=-2)).strftime("%Y-%m-%d")

        resp = await aiorequests.get('https://api.pixiv.hcyacg.com/public/ranking?ranking_type=illust&mode=daily_r18'
                                     '&date=' + nowtime + '&per_page=' + str(per_page) + '&page=' + str(page),
                                     headers=headers, timeout=10, stream=True)
        # 判断调用次数已超标
        if resp.status_code != 200:
            await bot.send(ev, f'[CQ:at,qq={userId}]' + '您的请求频率过快，请一分钟后再试')
            return
        res = await resp.json()

        # 访问详细接口
        illust = res['response'][0]['works'][int(number)]['work']['id']
        title = res['response'][0]['works'][int(number)]['work']['title']
        resp = await aiorequests.get(f'https://api.pixiv.hcyacg.com/illusts/detail?illustId={illust}&reduction=true',
                                     headers=headers, timeout=10, stream=True)

        if resp.status_code != 201:
            await bot.send(ev, f'[CQ:at,qq={userId}]' + '您的请求频率过快，请一分钟后再试')
            return
        res = await resp.json()
        page_count = res['data']['illust']['page_count']

        uri = None
        if page_count == 1:
            uri = res['data']['illust']['meta_single_page']['original_image_url'].replace("https://i.pximg.net", "https://i.pixiv.cat")
        else:
            meta_pages = res['data']['illust']['meta_pages']
            num = random.randint(1, len(meta_pages))
            uri = meta_pages[num-1]['image_urls']['original'].replace("https://i.pximg.net", "https://i.pixiv.cat")
        print(uri)

        req = urllib.request.Request(uri, None, {"cookie": "__cfduid=d0817de25eb2e728bf7ccad2ea09155ac1594917552","user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40"})
        file = urllib.request.urlopen(req)
        tmpIm = io.BytesIO(file.read())
        img = Image.open(tmpIm)
        suffix = img.format
        r = await aiorequests.get(uri, headers={"cookie": "__cfduid=d0817de25eb2e728bf7ccad2ea09155ac1594917552", "content-type": f"image/{suffix}", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40"}, stream=True)

        # 拼接图片路径
        path = AcgGov.get_path() + "/" + str(illust) + "." + suffix
        # 判断返回HTTP码是否为200
        if r.status_code == 200:
            # 写入本地并修改md5
            open(path, 'wb+').write(await r.content + bytes("jneth", encoding="utf8"))
            print("done")
            del r
        await bot.send(ev, f'[CQ:at,qq={userId}][CQ:image,file={illust}.{suffix}]\nid:{illust}\ntitle:{title}')
        os.remove(path)
    except Exception as e:
        sv.logger.error(f'Error: {e}')


def is_number(num):
    """
    判断是否为数字
    :param num:
    :return:
    """
    pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
    result = pattern.match(str(num))
    if result:
        return True
    else:
        return False
