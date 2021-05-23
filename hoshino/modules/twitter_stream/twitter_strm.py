import asyncio
import importlib
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, Set

import pytz
import peony
from peony import PeonyClient

import hoshino
from hoshino import Service, priv, util, sucmd
from hoshino.config import twitter as cfg
from hoshino.typing import MessageSegment as ms, CommandSession

try:
    import ujson as json
except:
    import json


sv = Service("twitter-poller", use_priv=priv.SUPERUSER, manage_priv=priv.SUPERUSER, visible=False)
bot = hoshino.get_bot()
daemon = None
follow_collection = [
    Service("twitter-stream-test", enable_on_default=False, manage_priv=priv.SUPERUSER, visible=False),
    Service("kc-twitter", help_="艦これ推特转发", enable_on_default=False, bundle="kancolle"),
    Service("pcr-twitter", help_="日服Twitter转发", enable_on_default=True, bundle="pcr订阅"),
    Service("uma-twitter", help_="ウマ娘推特转发", enable_on_default=False, bundle="umamusume"),
    Service("pripri-twitter", help_="番剧《公主代理人》官推转发", enable_on_default=False),
    Service("coffee-favorite-twitter", help_="咖啡精选画师推特转发", enable_on_default=False, bundle="artist"),
    Service("moe-artist-twitter", help_="萌系画师推特转发", enable_on_default=False, bundle="artist"),
    Service("depress-artist-twitter", help_="致郁系画师推特转发", enable_on_default=False, bundle="artist"),
]


@dataclass
class FollowEntry:
    services: Set[Service] = field(default_factory=set)
    media_only: bool = False
    profile_image: str = None


class TweetRouter:
    def __init__(self):
        self.follows: Dict[str, FollowEntry] = defaultdict(FollowEntry)

    def add(self, service: Service, follow_names: Iterable[str]):
        for f in follow_names:
            self.follows[f].services.add(service)

    def set_media_only(self, screen_name, media_only=True):
        if screen_name not in self.follows:
            raise KeyError(f"`{screen_name}` not in `TweetRouter.follows`.")
        self.follows[screen_name].media_only = media_only

    def load(self, service_follow_dict, media_only_users):
        for s in follow_collection:
            self.add(s, service_follow_dict[s.name])
        for x in media_only_users:
            self.set_media_only(x)


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
                sv.logger.error(f"{type(e)} occured when loading `twitter_uid_cache.json`, using empty cache.")

    async def convert(self, client: PeonyClient, screen_names: Iterable[str], cached=True):
        if not cached:
            self.cache = {}
        for i in screen_names:
            if i not in self.cache:
                user = await client.api.users.show.get(screen_name=i)
                self.cache[i] = user.id
        follow_ids = [self.cache[i] for i in screen_names]
        with open(self._cache_file, "w", encoding="utf8") as f:
            json.dump(self.cache, f)
        return follow_ids


def format_time(time_str):
    dt = datetime.strptime(time_str, r"%a %b %d %H:%M:%S %z %Y")
    dt = dt.astimezone(pytz.timezone("Asia/Shanghai"))
    return f"{util.month_name(dt.month)}{util.date_name(dt.day)}・{util.time_name(dt.hour, dt.minute)}"


def format_tweet(tweet):
    name = tweet.user.name
    time = format_time(tweet.created_at)
    text = tweet.text
    media = tweet.get("extended_entities", {}).get("media", [])
    imgs = " ".join([str(ms.image(m.media_url)) for m in media])
    msg = f"@{name}\n{time}\n\n{text}"
    if imgs:
        msg = f"{msg}\n{imgs}"
    return msg


@bot.on_startup
async def start_daemon():
    global daemon
    loop = asyncio.get_event_loop()
    daemon = loop.create_task(twitter_stream_daemon())


async def twitter_stream_daemon():
    client = PeonyClient(
        consumer_key=cfg.consumer_key,
        consumer_secret=cfg.consumer_secret,
        access_token=cfg.access_token_key,
        access_token_secret=cfg.access_token_secret,
    )
    async with client:
        while True:
            try:
                await open_stream(client)
            except (KeyboardInterrupt, asyncio.CancelledError):
                sv.logger.info("Twitter stream daemon exited.")
                return
            except Exception as e:
                sv.logger.exception(e)
                sv.logger.error(f"Error {type(e)} Occurred in twitter stream. Restarting stream in 5s.")
                await asyncio.sleep(5)


async def open_stream(client: PeonyClient):
    router = TweetRouter()
    router.load(cfg.follows, cfg.media_only_users)
    user_id_cache = UserIdCache()
    follow_ids = await user_id_cache.convert(client, router.follows)
    sv.logger.info(f"订阅推主={router.follows.keys()}, {follow_ids=}")
    stream = client.stream.statuses.filter.post(follow=follow_ids)
    async with stream:
        async for tweet in stream:

            sv.logger.info("Got twitter event.")
            if peony.events.tweet(tweet):
                screen_name = tweet.user.screen_name
                if screen_name not in router.follows:
                    continue    # 推主不在订阅列表
                if peony.events.retweet(tweet):
                    continue    # 忽略纯转推
                reply_to = tweet.get("in_reply_to_screen_name")
                if reply_to and reply_to != screen_name:
                    continue    # 忽略对他人的评论，保留自评论

                entry = router.follows[screen_name]
                media = tweet.get("extended_entities", {}).get("media", [])
                if entry.media_only and not media:
                    continue    # 无附带媒体，订阅选项media_only=True时忽略

                msg = format_tweet(tweet)

                if "quoted_status" in tweet:
                    quoted_msg = format_tweet(tweet.quoted_status)
                    msg = f"{msg}\n\n>>>>>\n{quoted_msg}"

                old_profile_img = entry.profile_image
                entry.profile_image = tweet.user.get("profile_image_url_https") or entry.profile_image
                if old_profile_img and entry.profile_image != old_profile_img:
                    big_img = re.sub(r'_normal(\.(jpg|jpeg|png|gif|jfif|webp))$', r'\1', entry.profile_image, re.I)
                    msg = [msg, f"@{screen_name} 更换了头像\n{ms.image(big_img)}"]

                sv.logger.info(f"推送推文：\n{msg}")
                for s in entry.services:
                    await s.broadcast(msg, f" @{screen_name} 推文", 0.2)

            else:
                sv.logger.debug("Ignore non-tweet event.")


@sucmd("reload-twitter-stream-daemon", force_private=False, aliases=("重启转推", "重载转推"))
async def reload_twitter_stream_daemon(session: CommandSession):
    try:
        daemon.cancel()
        importlib.reload(cfg)
        await start_daemon()
        await session.send('ok')
    except Exception as e:
        sv.logger.exception(e)
        await session.send(f'Error: {type(e)}')
