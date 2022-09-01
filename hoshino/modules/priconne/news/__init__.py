from hoshino import Service, util
from .spider import *

svtw = Service('pcr-news-tw', bundle='pcr订阅', help_='台服官网新闻')
svbl = Service('pcr-news-bili', bundle='pcr订阅', help_='B服官网新闻')
svjp = Service('pcr-news-jp', bundle='pcr订阅', help_='日服官网新闻')

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
    randomizer = util.randomizer(spider.src_name + '新闻')
    await sv.broadcast(spider.format_items(news), TAG, 0.5, randomizer)

@svtw.scheduled_job('cron', minute='*/5', jitter=20)
async def sonet_news_poller():
    await news_poller(SonetSpider, svtw, '台服官网')

@svbl.scheduled_job('cron', minute='*/5', jitter=20)
async def bili_news_poller():
    await news_poller(BiliSpider, svbl, 'B服官网')

@svjp.scheduled_job('cron', minute='*/5', jitter=20)
async def jp_news_poller():
    await news_poller(JpSpider, svjp, '日服官网')

async def send_news(bot, ev, spider:BaseSpider, max_num=5):
    if not spider.item_cache:
        await spider.get_update()
    news = spider.item_cache
    news = news[:min(max_num, len(news))]
    await bot.send(ev, spider.format_items(news), at_sender=True)

@svtw.on_fullmatch('台服新闻', '台服日程')
async def send_sonet_news(bot, ev):
    await send_news(bot, ev, SonetSpider)

@svbl.on_fullmatch('B服新闻', 'b服新闻', 'B服日程', 'b服日程')
async def send_bili_news(bot, ev):
    await send_news(bot, ev, BiliSpider)

@svjp.on_fullmatch(('日服新闻', '日服日程'))
async def send_jp_news(bot, ev):
    await send_news(bot, ev, JpSpider)
