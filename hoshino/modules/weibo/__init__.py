from .weibo import WeiboSpider
from hoshino.service import Service, Privilege as Priv
from hoshino.res import R
from hoshino import util
from .exception import *

'''
sample config.json

[{
    "service_name": "bcr-weibo",
    "enable_on_default": true,
    "users":[{
        "user_id": "6603867494",
        "alias": ["公主连接", "公主连结", "公主链接"],
        "filter": true
    }]
    
}]
'''

lmt = util.FreqLimiter(5)

def _load_config(services_config):
    for sv_config in services_config:
        sv.logger.debug(sv_config)
        service_name = sv_config["service_name"]
        enable_on_default = sv_config.get("enable_on_default", False)
        
        users_config = sv_config["users"]

        sv_spider_list = []
        for user_config in users_config:
            wb_spider = WeiboSpider(user_config)
            sv_spider_list.append(wb_spider)
            alias_list = user_config.get("alias", [])
            for alias in alias_list:
                if alias in alias_dic:
                    raise DuplicateError(f"Alias {alias} is duplicate")
                alias_dic[alias] = {
                    "service_name":service_name, 
                    "user_id":wb_spider.get_user_id()
                    }
        
        subService = Service(service_name, enable_on_default=enable_on_default)
        subr_dic[service_name] = {"service": subService, "spiders": sv_spider_list}

        
        
sv = Service('weibo-poller', use_priv=Priv.ADMIN, manage_priv=Priv.SUPERUSER, visible=False)
services_config = util.load_config(__file__)
subr_dic = {}
alias_dic = {}
_load_config(services_config)

def wb_to_message(wb):
    msg = f'@{wb["screen_name"]}'
    if "retweet" in wb:
        msg = f'{msg} 转发:\n{wb["text"]}\n======================'
        wb = wb["retweet"]
    else:
        msg = f'{msg}:'

    msg = f'{msg}\n{wb["text"]}'

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

# @bot 看微博 alias
@sv.on_command('看微博', only_to_me=True)
async def get_last_5_weibo(session):
    uid = session.ctx['user_id']
    if not lmt.check(uid):
        session.finish('您查询得过于频繁，请稍等片刻', at_sender=True)
    lmt.start_cd(uid)

    alias = session.current_arg_text
    if alias not in alias_dic:
        await session.finish(f"未找到微博: {alias}")
        return
    service_name = alias_dic[alias]["service_name"]
    user_id = alias_dic[alias]["user_id"]

    spiders = subr_dic[service_name]["spiders"]
    for spider in spiders:
        if spider.get_user_id() == user_id:
            last_5_weibos = spider.get_last_5_weibos()
            formatted_weibos = [wb_to_message(wb) for wb in last_5_weibos]
            for wb in formatted_weibos:
                await session.send(wb)
            await session.finish(f"以上为 {alias} 的最新 {len(formatted_weibos)} 条微博")
            return
    await session.finish(f"未找到微博: {alias}")

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

@sv.scheduled_job('interval', seconds=60*60*24)
async def clear_spider_buffer():
    sv.logger.info("Clearing weibo spider buffer...")
    for sv_name, serviceObj in subr_dic.items():
        spiders = serviceObj["spiders"]
        for spider in spiders:
            spider.clear_buffer()