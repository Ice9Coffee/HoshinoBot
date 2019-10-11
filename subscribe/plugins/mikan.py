import os
import ujson as json
import random
import requests
from lxml import etree
from datetime import datetime
from time import sleep

import nonebot
from nonebot import CommandSession, on_command
from aiocqhttp.exceptions import Error as CQHttpError


class Mikan(object):
    link_cache = set()
    rss_cache = []
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')

    @staticmethod
    def get_config():
        with open(Mikan.config_file, 'r') as f:
            config = json.load(f)
            return config


    @staticmethod
    def get_token():
        return Mikan.get_config()["MIKAN_TOKEN"]


    @staticmethod
    def get_auth_group():
        return Mikan.get_config()["MIKAN_GROUP"]


    @staticmethod
    def get_rss():
        res = []
        try:
            resp = requests.get('https://mikanani.me/RSS/MyBangumi', params={'token': Mikan.get_token()}, timeout=10)
            rss = etree.XML(resp.content)
        except Exception as e:
            print(f'[{datetime.now()}] get_rss Error: {e}')
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




@nonebot.scheduler.scheduled_job('cron', minute='0/3', second='15', jitter=4)
async def sche_lookup():
    # print(f'[{datetime.now()} 计划任务：sche_lookup] 启动')
    if not Mikan.rss_cache:
        Mikan.update_cache()
        print(f'[{datetime.now()} 计划任务：sche_lookup] 订阅缓存为空，已加载至最新')
        return

    new_bangumi = Mikan.update_cache()
    if new_bangumi:

        print(f'[{datetime.now()}] 检索到{len(new_bangumi)}条番剧更新！')

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

        bot = nonebot.get_bot()
        for group in Mikan.get_auth_group():
            sleep(1.0)  # 降低发送频率，避免被腾讯ban TODO: sleep 不够优雅，换一种解决方式
            try:
                for m in msg:
                    sleep(0.5)
                    await bot.send_group_msg(group_id=group, message=f'{random.choice(msg_device)}监测到番剧更新!{"!"*random.randint(0,4)}\n{m}')
                print(f'群{group} 投递成功')
            except CQHttpError as e:
                print(e)
                print(f'Error：群{group} 投递失败')
    else:
        print(f'[{datetime.now()}] 未检索到番剧更新！')

    # print(f'[{datetime.now()} 计划任务：sche_lookup] 完成')



@on_command('来点新番')
async def send_bangumi(session:CommandSession):
    if not Mikan.rss_cache:
        Mikan.update_cache()

    msg = [ f'{i[1]} 【{i[2].strftime(r"%Y-%m-%d %H:%M")}】\n▲链接 {i[0]}' for i in Mikan.rss_cache[:min(5, len(Mikan.rss_cache))] ]
    msg = '\n'.join(msg)
    await session.send(f'最近更新的番剧：\n{msg}')


if __name__ == "__main__":
    print(Mikan.get_rss())

