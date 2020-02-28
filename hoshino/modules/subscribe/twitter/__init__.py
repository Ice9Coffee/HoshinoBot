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

for _, ids in _subr_dic.items():
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
            'count': '10',
            'since_id': str(_latest_tweet_id[account])
        }
        rsp = await twt_request(_url_timeline, params)
        _update_latest_tweet_id(account, rsp)
        return list(map(lambda item: f"@{account}\n{item['created_at']}\n\n{item['text']}", rsp.get_iterator()))


@wraps(api.request)
async def twt_request(*args, **kwargs):
    return await asyncio.get_event_loop().run_in_executor(
        None, partial(api.request, *args, **kwargs))


# Requests/15-min window: 900  == 1 req/s
_subr_num = len(_latest_tweet_id)
_freq = 20 * _subr_num
sv.logger.info(f"twitter_poller works at {_subr_num} / {_freq} seconds")

@sv.scheduled_job('interval', seconds=_freq)
async def twitter_poller(_):
    bot = sv.bot
    buf = {}
    for account in _latest_tweet_id:
        try:
            buf[account] = await _poll_new_tweets(account)
            if l := len(buf[account]):
                sv.logger.info(f"成功获取@{account}的新推文{l}条")
            else:
                sv.logger.info(f"未检测到@{account}的新推文")
        except Exception as e:
            sv.logger.exception(e)
            sv.logger.error(f"获取@{account}的推文时出现异常{type(e)}")

    for ssv, subr_list in _subr_dic.items():
        groups = await ssv.get_enable_groups()
        for gid, selfs in groups.items():
            try:
                flag = False
                for account in subr_list:
                    twts = buf.get(account, [])
                    for twt in twts:
                        await asyncio.sleep(0.5)
                        await bot.send_group_msg(self_id=random.choice(selfs), group_id=gid, message=twt)
                        flag = True
                if flag:
                    ssv.logger.info(f'群{gid} 投递推特订阅成功')
            except Exception as e:
                ssv.logger.exception(e)
                ssv.logger.error(f'群{gid} 投递推特订阅失败 {type(e)}')
