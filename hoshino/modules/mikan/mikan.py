import random
from datetime import datetime

from lxml import etree

import hoshino
from hoshino import Service, aiorequests

sv = Service('bangumi', enable_on_default=False, help_='蜜柑番剧更新推送')

class Mikan:
    link_cache = set()
    rss_cache = []

    @staticmethod
    def get_token():
        return hoshino.config.mikan.MIKAN_TOKEN


    @staticmethod
    async def get_rss():
        res = []
        try:
            resp = await aiorequests.get('https://mikanani.me/RSS/MyBangumi', params={'token': Mikan.get_token()}, timeout=10)
            rss = etree.XML(await resp.content)
        except Exception as e:
            sv.logger.error(f'[get_rss] Error: {e}')
            return []

        for i in rss.xpath('/rss/channel/item'):
            link: str = i.find('./link').text
            link = link.replace("https://mikanani.me/Home/Episode/", "magnet:?xt=urn:btih:")
            description = i.find('./description').text
            pubDate = i.find('.//xmlns:pubDate', namespaces={'xmlns': 'https://mikanani.me/0.1/'}).text
            pubDate = pubDate[:19]
            pubDate = datetime.strptime(pubDate, r'%Y-%m-%dT%H:%M:%S')
            res.append( (link, description, pubDate) )
        return res


    @staticmethod
    async def update_cache():
        rss = await Mikan.get_rss()
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


DEVICES = [
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

@sv.scheduled_job('cron', minute='*/3', second='15')
async def mikan_poller():
    if not Mikan.rss_cache:
        await Mikan.update_cache()
        sv.logger.info(f'订阅缓存为空，已加载至最新')
        return
    new_bangumi = await Mikan.update_cache()
    if not new_bangumi:
        sv.logger.info(f'未检索到番剧更新！')
    else:
        sv.logger.info(f'检索到{len(new_bangumi)}条番剧更新！')
        msg = [ f'{i[1]} 【{i[2].strftime(r"%Y-%m-%d %H:%M")}】\n▲下载 {i[0]}' for i in new_bangumi ]
        randomiser = lambda m: f'{random.choice(DEVICES)}监测到番剧更新!{"!"*random.randint(0,4)}\n{m}'
        await sv.broadcast(msg, '蜜柑番剧', 0.5, randomiser)


DISABLE_NOTICE = '本群蜜柑番剧功能已禁用\n使用【启用 bangumi】以启用（需群管理）\n开启本功能后将自动推送字幕组更新'

@sv.on_fullmatch('来点新番')
async def send_bangumi(bot, ev):
    if not Mikan.rss_cache:
        await Mikan.update_cache()

    msg = [ f'{i[1]} 【{i[2].strftime(r"%Y-%m-%d %H:%M")}】\n▲链接 {i[0]}' for i in Mikan.rss_cache[:min(5, len(Mikan.rss_cache))] ]
    msg = '\n'.join(msg)
    await bot.send(ev, f'最近更新的番剧：\n{msg}')
