import os
import ujson as json
import random
import requests
import asyncio
from lxml import etree
from datetime import datetime

import nonebot
from nonebot import CommandSession, on_command

from hoshino.service import Service


sv = Service('bangumi', enable_on_default=False)

class Mikan(object):
    link_cache = set()
    rss_cache = []

    @staticmethod
    def get_token():
        config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_file, encoding='utf8') as f:
            config = json.load(f)
            return config["MIKAN_TOKEN"]


    @staticmethod
    def get_rss():
        res = []
        try:
            resp = requests.get('https://mikanani.me/RSS/MyBangumi', params={'token': Mikan.get_token()}, timeout=10)
            rss = etree.XML(resp.content)
        except Exception as e:
            sv.logger.error(f'[get_rss] Error: {e}')
            return []

        for i in rss.xpath('/rss/channel/item'):
            link = i.find('./link').text
            description = i.find('./description').text
            pubDate = i.find('.//xmlns:pubDate', namespaces={'xmlns': 'https://mikanani.me/0.1/'}).text
            pubDate = datetime.strptime(pubDate, r'%Y-%m-%dT%H:%M:%S')
            res.append( (link, description, pubDate) )
        return res


    @staticmethod
    def update_cache():
        rss = Mikan.get_rss()
        new_bangumi = []
        flag = False
        for item in rss:
            if item[0] not in Mikan.link_cache:
                flag = True
                new_bangumi.append(item)
        if flag:
            Mikan.link_cache = { item[0] for item in rss }
            Mikan.rss_cache = rss
        return new_bangumi




@sv.scheduled_job('cron', minute='*/3', second='15')
async def mikan_poller(group_list):
    
    if not Mikan.rss_cache:
        Mikan.update_cache()
        sv.logger.info(f'订阅缓存为空，已加载至最新')
        return

    new_bangumi = Mikan.update_cache()
    if new_bangumi:

        sv.logger.info(f'检索到{len(new_bangumi)}条番剧更新！')

        msg = [ f'{i[1]} 【{i[2].strftime(r"%Y-%m-%d %H:%M")}】\n▲链接 {i[0]}' for i in new_bangumi ]
        msg_device = [
            '22号对水上电探改四(后期调整型)',
            '15m二重测距仪+21号电探改二',
            'FuMO25 雷达',
            'SK+SG 雷达',
            'SG 雷达(初期型)',
            'GFCS Mk.37',
            '潜水舰搭载电探&逆探(E27)',
            'HF/DF+Type144/147 ASDIC',
            '三式指挥联络机(对潜)',
            'O号观测机改二',
            'S-51J改',
            '二式陆上侦察机(熟练)',
            '东海(九〇一空)',
            '二式大艇',
            'PBY-5A Catalina',
            '零式水上侦察机11型乙(熟练)',
            '紫云',
            'Ar196改',
            'Ro.43水侦',
            'OS2U',
            'S9 Osprey',
            '彩云(东加罗林空)',
            '彩云(侦四)',
            '试制景云(舰侦型)',
        ]

        for group, sid in group_list.items():
            await asyncio.sleep(1.0)  # 降低发送频率，避免被腾讯ban
            try:
                for m in msg:
                    await asyncio.sleep(0.5)
                    await sv.bot.send_group_msg(self_id=random.choice(sid), group_id=group, message=f'{random.choice(msg_device)}监测到番剧更新!{"!"*random.randint(0,4)}\n{m}')
                sv.logger.info(f'群{group} 投递番剧更新成功')
            except Exception as e:
                sv.logger.error(f'Error：群{group} 投递番剧更新失败 {type(e)}')
    else:
        sv.logger.info(f'未检索到番剧更新！')



@sv.on_command('来点新番', aliases=('來點新番', ))
async def send_bangumi(session:CommandSession):
    if not Mikan.rss_cache:
        Mikan.update_cache()

    msg = [ f'{i[1]} 【{i[2].strftime(r"%Y-%m-%d %H:%M")}】\n▲链接 {i[0]}' for i in Mikan.rss_cache[:min(5, len(Mikan.rss_cache))] ]
    msg = '\n'.join(msg)
    await session.send(f'最近更新的番剧：\n{msg}')


if __name__ == "__main__":
    """for test"""
    print(Mikan.get_rss())

