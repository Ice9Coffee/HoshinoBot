from .weibo import WeiboSpider
from hoshino.service import Service, Privilege as Priv
from hoshino.res import R
from hoshino import util

sv = Service('weibo-poller', use_priv=Priv.ADMIN, manage_priv=Priv.SUPERUSER, visible=False)
user_configs = util.load_config(__file__)
'''
sample config.json

[{
    "user_id": "6603867494",
    "service_name": "bcr-weibo",
    "filter": true
}]
'''

subr_dic = {}

for config in user_configs:
    sv.logger.debug(config)
    wb_spider = WeiboSpider(config)
    service_name = config["service_name"]

    if service_name not in subr_dic:
        subService = Service(service_name, enable_on_default=True)
        subr_dic[service_name] = {"service": subService, "spiders": [wb_spider]}
    else:
        subr_dic[service_name]["spiders"].append(wb_spider)

def wb_to_message(wb):
    msg = f'@{wb["screen_name"]}:\n{wb["text"]}'
    if sv.bot.config.IS_CQPRO and len(wb["pics"]) > 0:
        images_url = wb["pics"]
        msg = f'{msg}\n'
        res_imgs = [R.remote_img(url).cqcode for url in images_url]
        for img in res_imgs:
            msg = f'{msg}{img}'
    if len(wb["video_url"]) > 0:
        videos = wb["video_url"]
        res_videos = ';'.join(videos)
        msg = f'{msg}\n视频链接：{res_videos}'
    return msg

@sv.scheduled_job('interval', seconds=20*60)
async def weibo_poller():
    for sv_name, serviceObj in subr_dic.items():
        weibos = []
        ssv = serviceObj["service"]
        spiders = serviceObj["spiders"]
        for spider in spiders:
            latest_weibos = await spider.get_latest_weibos()
            formatted_weibos = [wb_to_message(wb) for wb in latest_weibos]

            if l := len(formatted_weibos):
                sv.logger.info(f"成功获取@{spider.get_username()}的新微博{l}条")
            else:
                sv.logger.info(f"未检测到@{spider.get_username()}的新微博")

            weibos.extend(formatted_weibos)
        await ssv.broadcast(weibos, ssv.name, 0.5)