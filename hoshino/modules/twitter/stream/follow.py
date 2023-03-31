# 订阅推主

import asyncio
import itertools
import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, Set

import peony
from peony import PeonyClient
from peony.exceptions import PeonyException

from hoshino import Service, priv
from hoshino.config import twitter as cfg
from hoshino.typing import MessageSegment as ms

from . import sv
from .util import format_tweet

service_collection = [
    Service("twitter-stream-test", enable_on_default=False, manage_priv=priv.SUPERUSER, visible=False),
    Service("kc-twitter", help_="艦これ推特转发", enable_on_default=False, bundle="kancolle"),
    Service("pcr-twitter", help_="日服Twitter转发", enable_on_default=True, bundle="pcr订阅"),
    Service("uma-twitter", help_="ウマ娘推特转发", enable_on_default=False, bundle="umamusume"),
    Service("pripri-twitter", help_="番剧《公主代理人》官推转发", enable_on_default=False),
    Service("coffee-favorite-twitter", help_="咖啡精选画师推特转发", enable_on_default=False, bundle="artist"),
    Service("moe-artist-twitter", help_="萌系画师推特转发", enable_on_default=False, bundle="artist"),
    Service("depress-artist-twitter", help_="致郁系画师推特转发", enable_on_default=False, bundle="artist"),
]


class UserIdCache:
    _cache_file = os.path.expanduser("~/.hoshino/twitter_uid_cache.json")

    def __init__(self) -> None:
        self.cache = {}
        if os.path.isfile(self._cache_file):
            try:
                with open(self._cache_file, "r", encoding="utf8") as f:
                    self.cache = json.load(f)
            except Exception as e:
                sv.logger.exception(e)
                sv.logger.error(f"{type(e)} occured when loading `~/.hoshino/twitter_uid_cache.json`, using empty cache.")

    def get(self, screen_name):
        return self.cache.get(screen_name)

    async def convert(self, client: PeonyClient, screen_names: Iterable[str], cached=True):

        if not cached:
            self.cache = {}

        ids = []
        for x in screen_names:
            if x not in self.cache:
                client = peony.BasePeonyClient(
                                   consumer_key=cfg.consumer_key,
                                   consumer_secret=cfg.consumer_secret,
                                   access_token=cfg.access_token_key,
                                   access_token_secret=cfg.access_token_secret,
                                   auth=peony.oauth.OAuth2Headers,
                                   api_version="2",
                                   proxy=cfg.proxy,
                                   suffix="")
                async with client:
                 try:
                     user = await client.api.users.by.username[x].get()
                     print(user)
                     self.cache[x] = user.get('data').id
                 except PeonyException as e:
                    sv.logger.error(f"{e} occurred when getting id of `{x}`")

            id_ = self.cache.get(x)
            if id_:
                ids.append(id_)

        with open(self._cache_file, "w", encoding="utf8") as f:
            json.dump(self.cache, f)

        return ids


_id_cache = UserIdCache()


@dataclass
class FollowEntry:
    services: Set[Service] = field(default_factory=set)
    profile_image: str = None
    media_only: bool = False
    forward_retweet: bool = False


class TweetRouter:
    def __init__(self):
        self.follows: Dict[int, FollowEntry] = defaultdict(FollowEntry)

    def add(self, service: Service, follow_names: Iterable[str]):
        for name in follow_names:
            id_ = _id_cache.get(name)
            if id_ is None:
                continue
            self.follows[id_].services.add(service)

    def set_media_only(self, screen_name, media_only=True):
        id_ = _id_cache.get(screen_name)
        if id_ in self.follows:
            self.follows[id_].media_only = media_only
        else:
            sv.logger.warning(f"No user named `{screen_name}` or `{screen_name}` not in follows. Ignore media_only set.")

    def set_forward_retweet(self, screen_name, forward_retweet=True):
        id_ = _id_cache.get(screen_name)
        if id_ in self.follows:
            self.follows[id_].forward_retweet = forward_retweet
        else:
            sv.logger.warning(f"No user named `{screen_name}` or `{screen_name}` not in follows. Ignore forward_retweet set.")

    def load(self, service_follow_dict, media_only_users, forward_retweet_users):
        for s in service_collection:
            self.add(s, service_follow_dict[s.name])
        for x in media_only_users:
            self.set_media_only(x)
        for x in forward_retweet_users:
            self.set_forward_retweet(x)


async def follow_stream():
    client = peony.BasePeonyClient(
        consumer_key=cfg.consumer_key,
        consumer_secret=cfg.consumer_secret,
        access_token=cfg.access_token_key,
        access_token_secret=cfg.access_token_secret,
        auth=peony.oauth.OAuth2Headers,
        api_version="2",
        proxy=cfg.proxy,
        suffix="",
    )
    async with client:
        print("dddd")
        follow_screen_names = set(itertools.chain(*cfg.follows.values()))
        follow_ids = await _id_cache.convert(client, follow_screen_names)
        router = TweetRouter()
        router.load(cfg.follows, cfg.media_only_users, cfg.forward_retweet_users)
        sv.logger.info(f"订阅推主={follow_screen_names}, {follow_ids=}")
        resp = await client.api.tweets.search.stream.rules.get()            #先获取上一次的规则
        data =resp.get('data')
        if  resp.get('data'):                                               #然后删除上一次的规则
            ids = list(map(lambda rule: data[0]["id"], data))
            payload = {"delete": {"ids": ids}}
            resp = await client.api.tweets.search.stream.rules.post(_json=payload)
        data = {'add': [{'value': "from:PSO2NGS_JP OR from:Pso2ngsB OR from:pso2_emg_hour"}]}#按我的逻辑填，将会跟踪这些人的数据流
        resp = await client.api.tweets.search.stream.rules.post(_json=data)  #写入新规则                         ，收到了才会判断是否开启了服务再广播，本来想写完先判断再跟踪的，现在不想写了
        fields = {
            "tweet.fields": ["created_at", "entities", "referenced_tweets","text","author_id"],
            "expansions":["author_id","attachments.media_keys"],
            "media.fields":["url","preview_image_url"],#md搞半天得要有上面的media_keys这个才生效
        }
        stream = client.api.tweets.search.stream.get.stream(**fields)        #启动stream流
        async for tweet in stream:
            sv.logger.info("Got twitter event.")
            if tweet.get('data'):
                uid =  tweet.get('data').author_id
                screen_name = tweet.get('includes')['users'][0]['name']
                if uid not in router.follows:
                    continue    # 推主不在订阅列表
                try:  
                   entry = router.follows[uid]
                except Exception as e:
                    print(e)
                if peony.events.retweet(tweet) and not entry.forward_retweet:
                    continue    # 除非配置制定，忽略纯转推
                if 'in_reply_to_user_id'in tweet.get('data'):######################################################我没测试这种情况，自行测试
                   if  tweet.get('data').in_reply_to_user_id != uid:
                       continue    # 忽略对他人的评论，保留自评论

                media= tweet.get('includes')['media']#############3333333333333333333333333333333333333333333333我没测试这种情况，自行测试
                if entry.media_only and not media:
                    continue    # 无附带媒体，订阅选项media_only=True时忽略'''
                msg = format_tweet(tweet)
                '''old_profile_img = entry.profile_image
                entry.profile_image = tweet.user.get("profile_image_url_https") or entry.profile_image
                if old_profile_img and entry.profile_image != old_profile_img:
                    big_img = re.sub(r'_normal(\.(jpg|jpeg|png|gif|jfif|webp))$', r'\1', entry.profile_image, re.I)
                    msg = [msg, f"@{screen_name} 更换了头像\n{ms.image(big_img)}"]'''

                sv.logger.info(f"推送推文：\n{msg}")
                for s in entry.services:
                    asyncio.get_event_loop().create_task(s.broadcast(msg, f" @{screen_name} 推文", 0.2))

            else:
                sv.logger.debug("Ignore non-tweet event.")

