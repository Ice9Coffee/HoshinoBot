# ref: https://github.com/TheWanderingCoel/WuhanPneumoniaBot

import re
import ujson as json
import asyncio
from urllib.parse import urljoin
from datetime import datetime

from nonebot import CommandSession, MessageSegment
from hoshino import aiorequests
from hoshino.service import Service

sv = Service('nCoV2019', enable_on_default=False)

_api = "https://lab.isaaclin.cn/nCoV/api/"
_timeout = 10

class nCoV2019:
    
    cache = { 'overall': {}, 'news': [], 'news_url': set() }

    @staticmethod
    async def get_overall():
        url = urljoin(_api, 'overall')
        rsp = await aiorequests.get(url, timeout=_timeout)
        j = await rsp.json()
        data = j['results'][0]
        nCoV2019.cache['overall'] = data
        return data


    @staticmethod
    async def _get_news():
        url = urljoin(_api, 'news')
        rsp = await aiorequests.get(url, timeout=_timeout)
        j = await rsp.json()
        data = j['results']
        return data


    @staticmethod
    async def update_news():
        news = await nCoV2019._get_news()
        new_ones = []
        for item in news:
            if item['sourceUrl'] not in nCoV2019.cache['news_url']:
                nCoV2019.cache['news_url'].add(item['sourceUrl'])
                new_ones.append(item)
        nCoV2019.cache['news'] = news
        return new_ones


    # @staticmethod
    # def get_distribution():
    #     resp = nCoV2019._get_content()
    #     reg = r'<script id="getAreaStat">.+?window.getAreaStat\s=\s(\[.+?\])\}catch\(e\)\{\}</script>'
    #     result = re.search(reg, resp).group(1)
    #     data = json.loads(result)
    #     return data


    # @staticmethod
    # def get_status(name):
    #     data = nCoV2019.get_distribution()
    #     for each in data:
    #         if name in each["provinceName"]:
    #             return each
    #         for city in each["cities"]:
    #             if name in city["cityName"]:
    #                 return each
    #     return None



@sv.on_command('咳咳', only_to_me=False)
async def cough(session:CommandSession):
    name = session.current_arg_text
    if name:    # look up province or city
        # data = nCoV2019.get_status(name)
        # if not data:
        #     return "未知省市"
        # info = '\n'.join([f"{city['cityName']} 确诊{city['confirmedCount']}例" for city in data['cities'] ])
        # text = f"新型冠状病毒肺炎疫情\n{info}\n💊 全国疫情 → t.cn/A6v1xgC0"
        # await session.send(text)
        await session.finish('省市查询维护中...')
    else:   # show overall
        if not nCoV2019.cache['overall']:
            await nCoV2019.get_overall()
        data = nCoV2019.cache['overall']
        data['updateTimeStr'] = datetime.fromtimestamp(data['updateTime'] / 1000).strftime(r'%Y-%m-%d %H:%M')
        data['pic1'] = MessageSegment.image(data['dailyPics'][0]) # 新增图
        data['pic2'] = MessageSegment.image(data['dailyPics'][2]) # 累积图
        data['pic3'] = MessageSegment.image(data['dailyPics'][3]) # 治愈死亡图
        text = "新型冠状病毒肺炎疫情\n更新时间：{updateTimeStr}\n确诊{confirmedCount}例(+{confirmedIncr})\n疑似{suspectedCount}例(+{suspectedIncr})\n重症{seriousCount}例(+{seriousIncr})\n死亡{deadCount}例(+{deadIncr})\n治愈{curedCount}例(+{curedIncr})\n{pic1!s}{pic2!s}{pic3!s}\n更多请见丁香园：ncov.dxy.cn/ncovh5/view/pneumonia".format(**data)
        await session.send(text)


def _make_msg(news_item):
    news_item['pubDateStr'] = datetime.fromtimestamp(news_item['pubDate'] / 1000).strftime(r'%Y-%m-%d %H:%M')
    return "{infoSource}：【{title}】{pubDateStr}\n{summary}\n▲{sourceUrl}".format(**news_item)


@sv.on_command('咳咳咳', only_to_me=False)
async def cough_news(session:CommandSession):
    # await nCoV2019.update_news()
    if not nCoV2019.cache['news']:
        await nCoV2019.update_news()
    news = nCoV2019.cache['news']
    msg = [ _make_msg(i) for i in news[:min(5, len(news))] ]
    msg = '\n'.join(msg)
    await session.send(f'新冠活动报告：\n{msg}')


@sv.scheduled_job('cron', minute='*/20', misfire_grace_time=10, coalesce=True)
async def overall_poller(group_list):
    await nCoV2019.get_overall()
    sv.logger.info('nCoV2019 overall 已更新')


@sv.scheduled_job('cron', minute='*/15', misfire_grace_time=10, coalesce=True)
async def news_poller(group_list):
    TAG = '2019-nCoV新闻'
    if not nCoV2019.cache['news']:
        await nCoV2019.update_news()
        sv.logger.info(f'{TAG}缓存为空，已加载至最新')
        return

    news = await nCoV2019.update_news()
    if news:
        sv.logger.info(f'检索到{len(news)}条新闻！')
        msg = [ _make_msg(i) for i in news ]

        bot = sv.bot
        for m in reversed(msg):
            await asyncio.sleep(10)     # 降低发送频率，避免被腾讯ban
            for group in group_list:
                try:
                    await asyncio.sleep(0.5)
                    await bot.send_group_msg(group_id=group, message=m)
                    sv.logger.info(f'群{group} 投递{TAG}成功')
                except Exception as e:
                    sv.logger.error(f'Error：群{group} 投递{TAG}更新失败 {type(e)}')
    else:
        sv.logger.info(f'未检索到{TAG}更新！')
