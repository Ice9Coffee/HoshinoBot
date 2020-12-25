import asyncio
import random
import re
from collections import defaultdict
from datetime import datetime
from functools import partial, wraps

import pytz
from nonebot import MessageSegment as ms
from TwitterAPI import TwitterAPI, TwitterResponse

from hoshino import util, Service, priv
from hoshino.typing import CQEvent
from hoshino.config import twitter as cfg

api = TwitterAPI(cfg.consumer_key, cfg.consumer_secret, cfg.access_token_key, cfg.access_token_secret)
sv = Service('twitter-poller', use_priv=priv.SUPERUSER, manage_priv=priv.SUPERUSER, visible=False)

URL_TIMELINE = 'statuses/user_timeline'

subr_dic = {
    Service('kc-twitter', enable_on_default=False, help_='艦これ官推转发', bundle='kancolle'): ['KanColle_STAFF', 'C2_STAFF', 'ywwuyi'],
    Service('pcr-twitter', enable_on_default=True, help_='日服Twitter转发', bundle='pcr订阅'): ['priconne_redive', 'priconne_anime'],
    Service('pripri-twitter', enable_on_default=False, visible=False): ['pripri_anime'],
    Service('coffee-favorite-twitter', manage_priv=priv.SUPERUSER,
            enable_on_default=False, visible=False): ['shiratamacaron', 'k_yuizaki', 'suzukitoto0323'],
}

latest_info = {}      # { account: {last_tweet_id: int, profile_image: str } }
for _, ids in subr_dic.items():     # initialize
    for account in ids:
        latest_info[account] = {'last_tweet_id': 0, 'profile_image': '', 'media_only': False}

for account in ('shiratamacaron', 'k_yuizaki', 'suzukitoto0323'):
    latest_info[account]['media_only'] = True


@wraps(api.request)
async def twt_request(*args, **kwargs):
    return await asyncio.get_event_loop().run_in_executor(
        None, partial(api.request, *args, **kwargs))


def update_latest_info(account:str, rsp:TwitterResponse):
    for item in rsp.get_iterator():
        if item['id'] > latest_info[account]['last_tweet_id']:
            latest_info[account]['last_tweet_id'] = item['id']
            if item['user']['screen_name'] == account:
                latest_info[account]['profile_image'] = item['user']['profile_image_url']


def time_formatter(time_str):
    dt = datetime.strptime(time_str, r"%a %b %d %H:%M:%S %z %Y")
    dt = dt.astimezone(pytz.timezone('Asia/Shanghai'))
    return f"{util.month_name(dt.month)}{util.date_name(dt.day)}・{util.time_name(dt.hour, dt.minute)}"


def tweet_formatter(item):
    name = item['user']['name']
    time = time_formatter(item['created_at'])
    text = item['full_text']
    try:
        img = item['entities']['media'][0]['media_url']
        assert re.search(r'\.(jpg|jpeg|png|gif|jfif|webp)$', img, re.I)
        img = f"\n{ms.image(img)}"
    except:
        img = ''
    return f"@{name}\n{time}\n\n{text}{img}"


def has_media(item):
    try:
        return bool(item['entities']['media'][0]['media_url'])
    except:
        return False


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
            'since_id': latest_info[account]['last_tweet_id'],
            'tweet_mode': 'extended',
            'include_rts': False,
        }
        rsp = await twt_request(URL_TIMELINE, params)
        old_profile_image = latest_info[account]['profile_image']
        update_latest_info(account, rsp)
        new_profile_image = latest_info[account]['profile_image']

        items = rsp.get_iterator()
        if latest_info[account]['media_only']:
            items = filter(has_media, items)
        tweets = list(map(tweet_formatter, items))
        if new_profile_image != old_profile_image and old_profile_image:
            big_img = re.sub(r'_normal(\.(jpg|jpeg|png|gif|jfif|webp))$', r'\1', new_profile_image, re.I)
            tweets.append(f"@{account} 更换了头像\n{ms.image(big_img)}")
        return tweets


# Requests/15-min window: 900  == 1 req/s
_subr_num = len(latest_info)
_freq = 8 * _subr_num
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
        if twts:
            await ssv.broadcast(twts, ssv.name, 0.5)


@sv.on_prefix('看推', only_to_me=True)     # for test
async def one_tweet(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    try:
        account = args[0]
    except:
        account = 'KanColle_STAFF'
    try:
        count = min(int(args[1]), 15)
        if count <= 0:
            count = 3
    except:
        count = 3
    params = {
        'screen_name': account,
        'count': count,
        'tweet_mode': 'extended',
    }
    rsp = await twt_request(URL_TIMELINE, params)
    items = rsp.get_iterator()
    if account in latest_info and latest_info[account]['media_only']:
        items = filter(has_media, items)
    twts = list(map(tweet_formatter, items))
    for t in twts:
        await bot.send(ev, t)
        await asyncio.sleep(0.5)
