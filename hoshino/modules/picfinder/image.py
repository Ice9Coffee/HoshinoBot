import asyncio
import requests
import re
import cloudscraper
from functools import partial

from lxml import etree
from io import BytesIO
from PIL import Image, ImageDraw
from random import randint
from traceback import format_exc

from hoshino import log, aiorequests
from hoshino.typing import CQEvent, MessageSegment
from hoshino.util import pic2b64

try:
    import ujson as json
except:
    import json

from hoshino.config.picfinder import SAUCENAO_RESULT_NUM, ASCII_RESULT_NUM, THUMB_ON, proxies, HOST_CUSTOM

from . import sv

logger = sv.logger


async def get_pic(address):
    return await (await aiorequests.get(address, timeout=20, proxies=proxies)).content


def randcolor():
    return (randint(0, 255), randint(0, 255), randint(0, 255))


def ats_pic(img):
    if(img.mode != 'RGB'):
        img = img.convert("RGB")
    width = img.size[0]-1  # 长度
    height = img.size[1]-1  # 宽度
    img.putpixel((0, 0), randcolor())
    img.putpixel((0, height), randcolor())
    img.putpixel((width, 0), randcolor())
    img.putpixel((width, height), randcolor())
    return img


async def check_screenshot(bot, file, imgurl):
    pichead = await aiorequests.head(imgurl)
    if pichead.headers['Content-Type'] == 'image/gif':
        print("gif pic, not likely a screen shot")
        return 0
    try:
        image = Image.open(BytesIO(await (await aiorequests.get(imgurl, stream=True)).content))
    except:
        print("download failed")
        return 0
    cord = image.size[0]/image.size[1]
    height = image.size[1]
    print(cord)
    if cord > 0.565:
        print("too short, not likely a screen shot")
        return 0
    if cord < 0.2:
        print("too long, might be long screen shot")
        return 2
    print("size checked, next ocr")
    try:
        ocr_result = await bot.call_action(action='.ocr_image', image=file)
    except:
        print("ocr failed")
        return False
    flag = 0
    for result in ocr_result['texts']:
        key1 = re.search('[0-9]{1,2}:[0-9]{2}', result['text'])  # 时间
        key2 = re.search('移动|联通|电信', result['text'])
        key3 = re.search('4G|5G', result['text'])
        key4 = re.search('[0-9]{1,2}%', result['text'])  # 电量
        key5 = re.search('[0-9]{0,3}[\\\/][0-9]{0,3}', result['text'])  # 页数
        if key2 or key3 or key4:
            print(str(result))
            loc = result['coordinates'][2]['y']
            if int(loc) < (int(height)/19):
                flag = 1
        if key1 or key5:
            print(str(result))
            loc = result['coordinates'][2]['y']
            if int(loc) < (int(height)/19) or int(loc) > (int(height)*18/20):
                flag = 1
        if flag:
            break
    if flag:
        #print(f"time mark found:{string}")
        return 1
    else:
        return 0


def sauces_info(sauce):
    service_name = ''
    info = ""
    try:
        if sauce['header']['index_id'] == 0:
            service_name = 'H-Magazines'
            title = sauce['data']['title']
            part = sauce['data']['part']
            date = sauce['data']['date']
            info = f"{title}-{part}/{date}"

        # index 1 "h-anime" disabled

        elif sauce['header']['index_id'] == 2:
            service_name = 'H-Game CG'
            # getchu_id=sauce['data']['getchu_id']
            company = sauce['data']['company']
            title = sauce['data']['title']
            info = f"[{company}] {title}"

        # index 3 "ddb-objects" disabled

        # index 4 "ddb-samples" disabled

        elif sauce['header']['index_id'] == 5 or sauce['header']['index_id'] == 6:
            service_name = 'pixiv'
            #member_id = sauce['data']['member_id']
            # illust_id=sauce['data']['pixiv_id']
            author_name = sauce['data']['member_name']
            title = sauce['data']['title']
            info = f"「{title}」/「{author_name}」"

        # index 6 "pixiv historical" with 5

        # index 7 "anime" disabled

        elif sauce['header']['index_id'] == 8:
            service_name = 'nico nico seiga'
            #member_id = sauce['data']['member_id']
            # illust_id=sauce['data']['seiga_id']
            author_name = sauce['data']['member_name']
            title = sauce['data']['title']
            info = f"「{title}」/「{author_name}」"

        elif sauce['header']['index_id'] == 9:
            service_name = 'Danbooru'
            # illust_id=sauce['data']['danbooru_id']
            #source = sauce['data']['source']
            creator = sauce['data']['creator']
            material = sauce['data']['material']
            info = f"[{creator}]({material})"

        elif sauce['header']['index_id'] == 10:
            service_name = 'drawr Images'
            #member_id = sauce['data']['member_id']
            # illust_id=sauce['data']['drawr_id']
            author_name = sauce['data']['member_name']
            title = sauce['data']['title']
            info = f"「{title}」/「{author_name}」"

        elif sauce['header']['index_id'] == 11:
            service_name = 'Nijie Images'
            #member_id = sauce['data']['member_id']
            # illust_id=sauce['data']['nijie_id']
            author_name = sauce['data']['member_name']
            title = sauce['data']['title']
            info = f"「{title}」/「{author_name}」"

        elif sauce['header']['index_id'] == 12:
            service_name = 'Yande.re'
            creator = sauce['data']['creator']
            # yandere_id=sauce['data']['yandere_id']
            material = sauce['data']['material']
            #source = sauce['data']['source']
            info = f"[{creator}]({material})"

        # index 13 "animeop" disabled

        # index 14 "IMDb" disabled

        # index 15 "Shutterstock" disabled

        elif sauce['header']['index_id'] == 16:
            service_name = 'FAKKU'
            creator = sauce['data']['creator']
            source = sauce['data']['source']
            info = f"[{creator}]({source})"

        # index 17 reserved

        elif sauce['header']['index_id'] == 18 or sauce['header']['index_id'] == 38:
            service_name = 'H-Misc (ehentai)'
            eng_name = sauce['data']['eng_name']
            jp_name = sauce['data']['jp_name']
            info = f"{jp_name}" if jp_name else f"{eng_name}"

        elif sauce['header']['index_id'] == 19:
            service_name = '2D-Market'
            creator = sauce['data']['creator']
            source = sauce['data']['source']
            info = f"[{creator}]({source})"

        elif sauce['header']['index_id'] == 20:
            service_name = 'MediBang'
            #member_id = sauce['data']['member_id']
            member_name = sauce['data']['member_name']
            title = sauce['data']['title']
            info = f"「{title}」/「{member_name}」"

        elif sauce['header']['index_id'] == 21:
            service_name = 'Anime'
            title = sauce['data']['source']
            #anidb_id = sauce['data']['anidb_aid']
            year = sauce['data']['year']
            part = sauce['data']['part']
            est_time = sauce['data']['est_time']
            time = est_time.split('/')[0]
            info = f"《{title}》/{year}\n第{part}集，{time}"

        elif sauce['header']['index_id'] == 22:
            service_name = 'H-Anime'
            title = sauce['data']['source']
            #anidb_id = sauce['data']['anidb_aid']
            year = sauce['data']['year']
            part = sauce['data']['part']
            est_time = sauce['data']['est_time']
            time = est_time.split('/')[0]
            info = f"《{title}》/{year}\n第{part}集，{time}"

        elif sauce['header']['index_id'] == 23:
            service_name = 'IMDb-Movies'
            title = sauce['data']['source']
            #imdb_id = sauce['data']['imdb_id']
            year = sauce['data']['year']
            #part = sauce['data']['part']
            est_time = sauce['data']['est_time']
            time = est_time.split('/')[0]
            info = f"《{title}》/{year}，{time}"

        elif sauce['header']['index_id'] == 24:
            service_name = 'IMDb-Shows'
            title = sauce['data']['source']
            #imdb_id = sauce['data']['imdb_id']
            year = sauce['data']['year']
            part = sauce['data']['part']
            est_time = sauce['data']['est_time']
            time = est_time.split('/')[0]
            info = f"《{title}》/{year}\n第{part}集，{time}"

        elif sauce['header']['index_id'] == 25:
            service_name = 'Gelbooru'
            # illust_id=sauce['data']['gelbooru_id']
            creator = sauce['data']['creator']
            material = sauce['data']['material']
            info = f"[{creator}]({material})"

        elif sauce['header']['index_id'] == 26:
            service_name = 'Konachan'
            creator = sauce['data']['creator']
            material = sauce['data']['material']
            # illust_id=sauce['data']['konachan_id']
            info = f"[{creator}]({material})"

        elif sauce['header']['index_id'] == 27:
            service_name = 'Sankaku Channel'
            # illust_id=sauce['data']['sankaku_id']
            creator = sauce['data']['creator']
            material = sauce['data']['material']
            info = f"[{creator}]({material})"

        elif sauce['header']['index_id'] == 28:
            service_name = 'Anime-Pictures.net'
            # illust_id=sauce['data']['anime-pictures_id']
            creator = sauce['data']['creator']
            material = sauce['data']['material']
            info = f"[{creator}]({material})"

        elif sauce['header']['index_id'] == 29:
            service_name = 'e621.net'
            creator = sauce['data']['creator']
            # e621_id=sauce['data']['e621_id']
            material = sauce['data']['material']
            info = f"[{creator}]({material})"

        elif sauce['header']['index_id'] == 30:
            service_name = 'Idol Complex'
            creator = sauce['data']['creator']
            # idol_id=sauce['data']['idol_id']
            material = sauce['data']['material']
            info = f"[{creator}]({material})"

        elif sauce['header']['index_id'] == 31:
            service_name = 'bcy.net Illust'
            #member_id = sauce['data']['member_id']
            # illust_id=sauce['data']['bcy_id']
            author_name = sauce['data']['member_name']
            title = sauce['data']['title']
            info = f"「{title}」/「{author_name}」"

        elif sauce['header']['index_id'] == 32:
            service_name = 'bcy.net Cosplay'
            #member_id = sauce['data']['member_id']
            # illust_id=sauce['data']['bcy_id']
            author_name = sauce['data']['member_name']
            title = sauce['data']['title']
            info = f"「{title}」/「{author_name}」"

        elif sauce['header']['index_id'] == 33:
            service_name = 'PortalGraphics.net'
            # illust_id=sauce['data']['pg_id']
            #member_id = sauce['data']['member_id']
            member_name = sauce['data']['member_name']
            title = sauce['data']['title']
            info = f"「{title}」/「{member_name}」"

        elif sauce['header']['index_id'] == 34:
            service_name = 'deviantArt'
            # illust_id=sauce['data']['da_id']
            author_name = sauce['data']['author_name']
            title = sauce['data']['title']
            info = f"「{title}」/「{author_name}」"

        elif sauce['header']['index_id'] == 35:
            service_name = 'Pawoo.net'
            illust_id = sauce['data']['pawoo_id']
            #member_id = sauce['data']['pawoo_user_acct']
            author_name = sauce['data']['pawoo_user_display_name']
            info = f"「{illust_id}」/「{author_name}」"

        elif sauce['header']['index_id'] == 36:
            service_name = 'Madokami (Manga)'
            source = sauce['data']['source']
            part = sauce['data']['part']

            info = part if source in part else f"{source}-{part}"

        elif sauce['header']['index_id'] == 37 or sauce['header']['index_id'] == 371:
            service_name = 'MangaDex'
            # illust_id=sauce['data']['md_id']
            artist = sauce['data']['artist']
            author = sauce['data']['author']
            source = sauce['data']['source']
            part = sauce['data']['part']
            info_a = f"[{artist}]" if artist == author else f"[{artist}({author})]"
            info_b = part if source in part else f"{source}-{part}"
            info = info_a+info_b

        # index 38 "H-Misc (ehentai)" with 18

        elif sauce['header']['index_id'] == 39:
            service_name = 'Artstation'
            #member_id = sauce['data']['author_url']
            # illust_id=sauce['data']['as_project']
            author_name = sauce['data']['author_name']
            title = sauce['data']['title']
            info = f"「{title}」/「{author_name}」"

        elif sauce['header']['index_id'] == 40:
            service_name = 'FurAffinity'
            #member_id = sauce['data']['fa_id']
            author_name = sauce['data']['author_name']
            title = sauce['data']['title']
            info = f"「{title}」/「{author_name}」"

        elif sauce['header']['index_id'] == 41:
            service_name = 'Twitter'
            #member_id = sauce['data']['twitter_user_id']
            # illust_id=sauce['data']['tweet_id']
            author_name = sauce['data']['twitter_user_handle']
            time = sauce['data']['created_at']
            info = f"「{time[0:10]}」/「{author_name}」"

        elif sauce['header']['index_id'] == 42:
            service_name = 'Furry Network'
            #illust_id = sauce['data']['fn_id']
            author_name = sauce['data']['author_name']
            title = sauce['data']['title']
            info = f"「{title}」/「{author_name}」"

        elif sauce['header']['index_id'] == 43:
            service_name = 'Kemono'
            #illust_id = sauce['data']['id']
            service = sauce['data']['service_name']
            author_name = sauce['data']['user_name']
            title = sauce['data']['title']
            info = f"「{title}」/「({service}){author_name}」"

        elif sauce['header']['index_id'] == 44:
            service_name = 'Skeb'
            #illust_id = sauce['data']['id']
            creator_name = sauce['data']['creator_name']
            creator = sauce['data']['creator']
            info = f"[{creator_name}]({creator})"

        else:
            index = sauce['header']['index_id']
            service_name = f'Index #{index}'
            info = "no info"

    except Exception as e:
        index = sauce['header']['index_id']
        service_name = f'Index #{index}'
        info = "no info"
        logger.exception(e)


    return service_name, info


class SauceNAO():
    def __init__(self, api_key, output_type=2, testmode=0, dbmask=None, dbmaski=None, db=999, numres=3, shortlimit=20, longlimit=300):
        params = dict()
        params['api_key'] = api_key
        params['output_type'] = output_type
        params['testmode'] = testmode
        params['dbmask'] = dbmask
        params['dbmaski'] = dbmaski
        params['db'] = db
        params['numres'] = numres
        self.params = params
        self.host = HOST_CUSTOM['SAUCENAO'] or 'https://saucenao.com'
        self.header = "————>saucenao<————"

    async def get_sauce(self, url):
        self.params['url'] = url
        logger.debug(f"Now starting get the SauceNAO data:{url}")
        response = await aiorequests.get(f'{self.host}/search.php', params=self.params, timeout=15, proxies=proxies)
        data = await response.json()

        return data

    async def get_view(self, sauce) -> str:
        sauces = await self.get_sauce(sauce)
        repass = ""
        simimax = 0

        for sauce in sauces['results']:
            try:
                url = sauce['data']['ext_urls'][0].replace(
                    "\\", "").strip() if 'ext_urls' in sauce['data'] else "no link"
                similarity = sauce['header']['similarity']
                if not similarity.replace(".", "").isdigit():
                    # print(sauce)
                    similarity = 0
                simimax = float(similarity) if float(similarity) > simimax else simimax
                thumbnail_url = sauce['header']['thumbnail']
                if THUMB_ON:
                    try:
                        thumbnail_image = str(MessageSegment.image(pic2b64(ats_pic(Image.open(BytesIO(await get_pic(thumbnail_url)))))))
                    except Exception as e:
                        logger.exception(e)
                        thumbnail_image = "[预览图下载失败]"
                else:
                    thumbnail_image = ""

                service_name, info = sauces_info(sauce)

                putline = f"{thumbnail_image}\n[{service_name}][{url}] 相似度:{similarity}%\n{info}"
                if repass:
                    repass = "\n".join([repass, putline])
                else:
                    repass = putline

            except Exception as e:
                logger.exception(e)
                # print(sauce)
                pass

        return [repass, simimax]


class ascii2d():
    def __init__(self, num=2):
        self.num = num
        self.host = HOST_CUSTOM['ASCII'] or "https://ascii2d.net"
        self.header = "————>ascii2d<————"
        self.scraper = cloudscraper.create_scraper()

    async def get_search_data(self, url: str, data=None):
        if data is not None:
            html = data
        else:
            # html_data = await aiorequests.get(url, timeout=15, proxies=proxies)
            # html = etree.HTML(await html_data.text)
            html_data = await asyncio.get_running_loop().run_in_executor(None, partial(self.scraper.get, url, timeout=15, proxies=proxies))
            html = etree.HTML(html_data.text)

        all_data = html.xpath('//div[@class="row item-box"]')
        info = []
        for data in all_data[1:self.num+1]:
            try:
                title = ""
                member = ""
                if not data.xpath('.//img[@loading="lazy"]/@src'):
                    continue
                thumb_url = data.xpath('.//img[@loading="lazy"]/@src')[0].strip()
                thumb_url = f"{self.host}{thumb_url}"

                if not data.xpath('.//div[@class="detail-box gray-link"]/h6'):
                    data2 = data.xpath(
                        './/div[@class="external"]')[0] if data.xpath('.//div[@class="external"]') else data
                    info_url = data2.xpath('.//a/@href')[0].strip() if data.xpath('.//a/@rel') else "no link"
                    tag = "外部登录" if info_url == "no link" else info_url.split('/')[2]
                else:
                    data2 = data.xpath('.//div[@class="detail-box gray-link"]/h6')[0]
                    info_url = data2.xpath(".//a/@href")[0].strip()
                    tag = (data2.xpath("./small/text()") or data2.xpath(".//a/text()"))[0].strip()

                if tag == "pixiv" or tag == "twitter":
                    title = data2.xpath(".//a//text()")[0]
                    member = data2.xpath(".//a//text()")[1]
                    title = f"「{title}」/「{member}」"
                elif tag == "外部登录":
                    title = data2.text.replace("\n", "") if data2.text else ""
                else:
                    title = data2.text.replace("\n", "")
                    title = f"「{title}」"

                info.append([info_url, tag, thumb_url, title])
            except Exception as e:
                logger.exception(e)
                continue

        return info

    async def add_repass(self, tag: str, data):
        po = "——{}——".format(tag)
        for line in data:
            if THUMB_ON:
                try:
                    # thumbnail_image = str(MessageSegment.image(pic2b64(ats_pic(Image.open(BytesIO(await get_pic(line[2])))))))
                    thumbnail_image = await asyncio.get_running_loop().run_in_executor(None, partial(self.scraper.get, line[2], timeout=20, proxies=proxies))
                    thumbnail_image = str(MessageSegment.image(
                        pic2b64(ats_pic(Image.open(BytesIO(thumbnail_image.content))))))
                except Exception as e:
                    logger.exception(e)
                    thumbnail_image = "[预览图下载失败]"
            else:
                thumbnail_image = ""
            putline = f"{thumbnail_image}\n[{line[1]}][{line[0]}]\n{line[3]}"
            po = "\n".join([po, putline])

        return po

    async def get_view(self, ascii2d) -> str:
        putline1 = ''
        putline2 = ''
        url_index = f"{self.host}/search/url/{ascii2d}"
        logger.debug(f"Now starting get the {url_index}")

        try:
            # html_index_data = await aiorequests.get(url_index, timeout=7, proxies=proxies)
            # html_index = etree.HTML(await html_index_data.text)
            html_index_data = await asyncio.get_running_loop().run_in_executor(None, partial(self.scraper.get, url_index, timeout=7, proxies=proxies))
            html_index = etree.HTML(html_index_data.text)
        except Exception as e:
            logger.error(f"ascii2d get html data failed: {e}")
            logger.exception(e)
            return [putline1, putline2]

        neet_div = html_index.xpath('//div[@class="detail-link pull-xs-right hidden-sm-down gray-link"]')

        if neet_div:

            a_url_foot = neet_div[0].xpath('./span/a/@href')
            url2 = f"{self.host}{a_url_foot[1]}"

            color = await self.get_search_data('', data=html_index)
            bovw = await self.get_search_data(url2)

            if color:
                putline1 = await self.add_repass("色调检索", color)

            if bovw:
                putline2 = await self.add_repass("特征检索", bovw)

        return [putline1, putline2]


async def get_image_data_sauce(image_url: str, api_key: str):
    if type(image_url) == list:
        image_url = image_url[0]

    logger.info("Loading Image Search Container……")
    NAO = SauceNAO(api_key, numres=SAUCENAO_RESULT_NUM)

    logger.debug("Loading all view……")
    repass = ''
    simimax = 0
    try:
        result = await NAO.get_view(image_url)
        if result:
            header = NAO.header
            simimax = result[1]
            repass = "\n".join([header, result[0]])
    except Exception as e:
        logger.exception(e)
        return ["SauceNAO搜索失败……", 0]

    return [repass, simimax]


async def get_image_data_ascii(image_url: str):
    if type(image_url) == list:
        image_url = image_url[0]

    logger.info("Loading Image Search Container……")
    ii2d = ascii2d(ASCII_RESULT_NUM)

    logger.debug("Loading all view……")
    repass1 = ''
    repass2 = ''
    try:
        putline = await ii2d.get_view(image_url)
        if putline:
            header = ii2d.header
            if putline[0]:
                repass1 = "\n".join([header, putline[0]])
            if putline[1]:
                repass2 = "\n".join([header, putline[1]])
    except Exception as e:
        logger.exception(e)
        return ["ascii2d搜索失败……", ""]

    return [repass1, repass2]
