import pytz
import random
import asyncio
from datetime import datetime
from functools import partial, wraps
from collections import defaultdict
from TwitterAPI import TwitterAPI, TwitterResponse

from nonebot import MessageSegment as ms
from hoshino import util
from hoshino.service import Service, Privilege as Priv

cfg = util.load_config(__file__)
api = TwitterAPI(cfg['consumer_key'], cfg['consumer_secret'], cfg['access_token_key'], cfg['access_token_secret'])
sv = Service('twitter-poller', enable_on_default=True, manage_priv=Priv.SUPERUSER, visible=False)

URL_TIMELINE = 'statuses/user_timeline'

subr_dic = {
    Service('kc-twitter', enable_on_default=False): ['KanColle_STAFF', 'C2_STAFF', 'ywwuyi'],
    Service('pcr-twitter', enable_on_default=False): ['priconne_redive'],
    Service('pripri-twitter', enable_on_default=False): ['pripri_anime'],
}

latest_info = {}      # { account: {last_tweet_id: int, profile_image: str } }
for _, ids in subr_dic.items():     # initialize
    for account in ids:
        latest_info[account] = {'last_tweet_id': 0, 'profile_image': ''}


def update_latest_info(account:str, rsp:TwitterResponse):
    for item in rsp.get_iterator():
        if item['id'] > latest_info[account]['last_tweet_id']:
            latest_info[account]['last_tweet_id'] = item['id']
            if item['user']['screen_name'] == account:
                latest_info[account]['profile_image'] = item['user']['profile_image_url']


def time_formatter(time_str):
    dt = datetime.strptime(time_str, r"%a %b %d %H:%M:%S %z %Y")
    dt = dt.astimezone(pytz.timezone('Asia/Shanghai'))
    return f"{util.month_name(dt.month)}{util.date_name(dt.day)} {util.time_name(dt.hour, dt.minute)}"


async def poll_new_tweets(account:str):
    if not latest_info[account]['last_tweet_id']:   # on the 1st time
        params = {'screen_name': account, 'count': '1'}
        rsp = await twt_request(URL_TIMELINE, params)
        update_latest_info(account, rsp)
        return []
    else:       # on other times
        params = {
            'screen_name': account,
            'count': '10',
            'since_id': str(latest_info[account]['last_tweet_id']),
            'tweet_mode': 'extended',        
        }
        rsp = await twt_request(URL_TIMELINE, params)
        old_profile_image = latest_info[account]['profile_image']
        update_latest_info(account, rsp)
        new_profile_image = latest_info[account]['profile_image']
        
        tweets = list(map(lambda item: f"@{item['user']['name']}\n{time_formatter(item['created_at'])}\n\n{item['full_text']}", rsp.get_iterator()))
        if new_profile_image != old_profile_image:
            tweets.append(f"@{account} 更换了头像\n{ms.image(new_profile_image)}")
        return tweets


@wraps(api.request)
async def twt_request(*args, **kwargs):
    return await asyncio.get_event_loop().run_in_executor(
        None, partial(api.request, *args, **kwargs))


# Requests/15-min window: 900  == 1 req/s
_subr_num = len(latest_info)
_freq = 10 * _subr_num
sv.logger.info(f"twitter_poller works at {_subr_num} / {_freq} seconds")

@sv.scheduled_job('interval', seconds=_freq)
async def twitter_poller():
    buf = {}
    for account in latest_info:
        try:
            buf[account] = await poll_new_tweets(account)
            if l := len(buf[account]):
                sv.logger.info(f"成功获取@{account}的新推文{l}条")
            else:
                sv.logger.info(f"未检测到@{account}的新推文")
        except Exception as e:
            sv.logger.exception(e)
            sv.logger.error(f"获取@{account}的推文时出现异常{type(e)}")

    for ssv, subr_list in subr_dic.items():
        twts = []
        for account in subr_list:
            twts.extend(buf.get(account, []))
        await ssv.broad_cast(twts, ssv.name, 0.5)
