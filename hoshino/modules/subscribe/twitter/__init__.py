import random
import asyncio
from functools import partial, wraps
from collections import defaultdict
from TwitterAPI import TwitterAPI, TwitterResponse

from hoshino import util
from hoshino.service import Service, Privilege as Priv

cfg = util.load_config(__file__)
api = TwitterAPI(cfg['consumer_key'], cfg['consumer_secret'], cfg['access_token_key'], cfg['access_token_secret'])
sv = Service('twitter-poller', enable_on_default=True, manage_priv=Priv.SUPERUSER, visible=False)

_url_timeline = 'statuses/user_timeline'
_latest_tweet_id = {}      # { account: tweet_id }
_subr_dic = {
    Service('kc-twitter', enable_on_default=False): ['KanColle_STAFF', 'C2_STAFF'],
    Service('pcr-twitter', enable_on_default=False): ['priconne_redive'] 
}

for ids in _subr_dic:
    for account in ids:
        _latest_tweet_id[account] = 0   # initialize


def _update_latest_tweet_id(account:str, rsp:TwitterResponse):
    for item in rsp.get_iterator():
        _latest_tweet_id[account] = max(_latest_tweet_id[account], item['id'])


async def _poll_new_tweets(account:str):
    if not _latest_tweet_id[account]:   # on the 1st time
        params = {'screen_name': account, 'count': '1'}
        rsp = await twt_request(_url_timeline, params)
        _update_latest_tweet_id(account, rsp)
        return []
    else:       # on other times
        params = {
            'screen_name': account,
            'count': '5',
            'since_id': str(_latest_tweet_id[account])
        }
        rsp = await twt_request(_url_timeline, params)
        _update_latest_tweet_id(account, rsp)
        return map(lambda item: f"@{account}\n{item['created_at']}\n\n{item['text']}", rsp.get_iterator())


@wraps(api.request)
async def twt_request(*args, **kwargs):
    return await asyncio.get_event_loop().run_in_executor(
        None, partial(api.request, *args, **kwargs))


# Requests/15-min window: 900
@sv.scheduled_job('interval', minutes=1)
async def twitter_poller(_):
    bot = sv.bot
    buf = {}
    for account in _latest_tweet_id:
        try:
            buf[account] = await _poll_new_tweets(account)
            sv.logger.info(f"获取到{len(buf[account])}条@{account}的推文")
        except Exception as e:
            sv.logger.exception(e)
            sv.logger.error(f"获取@{account}的推文时出现异常{type(e)}")

    for ssv, subr_list in _subr_dic.items():
        groups = await ssv.get_enable_groups()
        for gid, selfs in groups.items():
            try:
                for account in subr_list:
                    twts = buf.get(account, [])
                    for twt in twts:
                        await bot.send_group_msg(self_id=random.choice(selfs), group_id=gid, message=twt)
                ssv.logger.info(f'群{gid} 投递推特订阅成功')
            except Exception as e:
                ssv.logger.exception(e)
                ssv.logger.error(f'群{gid} 投递推特订阅失败 {type(e)}')
