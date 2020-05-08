from hoshino import Service
from .spider import *

svtw = Service('pcr-news-tw')
svbl = Service('pcr-news-bili')

async def news_poller(spider:BaseSpider, sv:Service, TAG):
    if not spider.item_cache:
        await spider.get_update()
        sv.logger.info(f'{TAG}新闻缓存为空，已加载至最新')
        return
    news = await spider.get_update()
    if not news:
        sv.logger.info(f'未检索到{TAG}新闻更新')
        return
    sv.logger.info(f'检索到{len(news)}条{TAG}新闻更新！')
    await sv.broadcast(spider.format_items(news), TAG, interval_time=0.5)
    
@svtw.scheduled_job('cron', minute='*/20', jitter=20)
async def sonet_news_poller():
    await news_poller(SonetSpider, svtw, '台服官网')

@svbl.scheduled_job('cron', minute='*/20', jitter=20)
async def bili_news_poller():
    await news_poller(SonetSpider, svbl, 'B服官网')


async def send_news(session, spider:BaseSpider, max_num=5):
    if not spider.item_cache:
        await spider.get_update()
    news = spider.item_cache
    news = news[:min(max_num, len(news))]
    await session.send(spider.format_items(news), at_sender=True)

@svtw.on_command('台服新闻', aliases=('台服日程'))
async def send_sonet_news(session):
    await send_news(session, SonetSpider)

@svbl.on_command('B服新闻', aliases=('B服日程'))
async def send_bili_news(session):
    await send_news(session, BiliSpider)
