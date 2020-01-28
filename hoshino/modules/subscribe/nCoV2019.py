# ref: https://github.com/TheWanderingCoel/WuhanPneumoniaBot

import re
import requests
import ujson as json
import time
import asyncio

from nonebot import CommandSession, MessageSegment
from hoshino.service import Service

sv = Service('nCoV2019', enable_on_default=False)


class nCoV2019:
    
    url = "https://3g.dxy.cn/newh5/view/pneumonia"
    news_cache = []
    news_id_cache = set()

    @staticmethod
    def _get_content():
        return requests.get(nCoV2019.url, timeout=5).content.decode("utf-8")

    @staticmethod
    def get_overview():
        resp = nCoV2019._get_content()
        reg = r'<script id="getStatisticsService">.+?window.getStatisticsService\s=\s(.+?)\}catch\(e\)\{\}</script>'
        result = re.search(reg, resp).group(1)
        data = json.loads(result)
        return data


    @staticmethod
    def get_news():
        resp = nCoV2019._get_content()
        reg = r'<script id="getTimelineService">.+?window.getTimelineService\s=\s(\[.+?\])\}catch\(e\)\{\}</script>'
        result = re.search(reg, resp).group(1)
        data = json.loads(result)
        return data


    @staticmethod
    def update_news():
        news = nCoV2019.get_news()
        new_ones = []
        for item in news:
            if item['id'] not in nCoV2019.news_id_cache:
                nCoV2019.news_id_cache.add(item['id'])
                new_ones.append(item)
        nCoV2019.news_cache = news
        return new_ones


    @staticmethod
    def get_distribution():
        resp = nCoV2019._get_content()
        reg = r'<script id="getAreaStat">.+?window.getAreaStat\s=\s(\[.+?\])\}catch\(e\)\{\}</script>'
        result = re.search(reg, resp).group(1)
        data = json.loads(result)
        return data


    @staticmethod
    def get_status(name):
        data = nCoV2019.get_distribution()
        for each in data:
            if name in each["provinceName"]:
                return each
            for city in each["cities"]:
                if name in city["cityName"]:
                    return each
        return None



@sv.on_command('咳咳', only_to_me=False)
async def cough(session:CommandSession):
    name = session.current_arg_text
    if name:    # look up province or city
        data = nCoV2019.get_status(name)
        if not data:
            return "未知省市"
        info = '\n'.join([f"{city['cityName']} 确诊{city['confirmedCount']}例" for city in data['cities'] ])
        text = f"新型冠状病毒肺炎疫情\n{info}\n💊 全国疫情 → t.cn/A6v1xgC0"
        await session.send(text)

    else:   # show overview
        data = nCoV2019.get_overview()
        text = f"新型冠状病毒肺炎疫情\n确诊{data['confirmedCount']}例  疑似{data['suspectedCount']}例  死亡{data['deadCount']}例  治愈{data['curedCount']}例\n{MessageSegment.image(data['dailyPic'])}"
        await session.send(text)


@sv.on_command('咳咳咳', only_to_me=False)
async def cough_news(session:CommandSession):
    nCoV2019.update_news()
    msg = [ f"{i['infoSource']}：【{i['title']}】{i['pubDateStr']}\n{i['summary']}" for i in nCoV2019.news_cache[:min(5, len(nCoV2019.news_cache))] ]
    msg = '\n'.join(msg)
    await session.send(f'新冠活动报告：\n{msg}')


@sv.scheduled_job('cron', minute='*/15', misfire_grace_time=10, coalesce=True)
async def news_poller(group_list):

    TAG = '2019-nCoV新闻'
    
    if not nCoV2019.news_cache:
        nCoV2019.update_news()
        sv.logger.info(f'{TAG}缓存为空，已加载至最新')
        return

    news = nCoV2019.update_news()
    if news:
        sv.logger.info(f'检索到{len(news)}条新闻！')
        msg = [ f"{i['infoSource']}：【{i['title']}】{i['pubDateStr']}\n{i['summary']}" for i in news ]

        bot = sv.bot
        for m in reversed(msg):
            await asyncio.sleep(10) # 降低发送频率，避免被腾讯ban
            for group in group_list:
                try:
                    await asyncio.sleep(0.5)  
                    await bot.send_group_msg(group_id=group, message=m)
                    sv.logger.info(f'群{group} 投递{TAG}成功')
                except Exception as e:
                    sv.logger.error(f'Error：群{group} 投递{TAG}更新失败 {type(e)}')
    else:
        sv.logger.info(f'未检索到{TAG}更新！')
