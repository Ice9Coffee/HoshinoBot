import asyncio
from dataclasses import dataclass, field
from typing import Dict, Iterable, Set
from datetime import datetime

import pytz
import peony
from peony import PeonyClient

from hoshino import Service, priv, util
import hoshino
from hoshino.config import twitter as cfg
from hoshino.typing import MessageSegment as ms


@dataclass
class FollowEntry:
    services: Set[Service] = field(default_factory=set)
    media_only: bool = False


class TweetRouter:
    def __init__(self):
        self.follows: Dict[str, FollowEntry] = {}

    def add(self, service: Service, follow_names: Iterable[str]):
        for f in follow_names:
            if f not in self.follows:
                self.follows[f] = FollowEntry()
            self.follows[f].services.add(service)

    def set_media_only(self, screen_name, media_only=True):
        self.follows[screen_name].media_only = media_only


def format_time(time_str):
    dt = datetime.strptime(time_str, r"%a %b %d %H:%M:%S %z %Y")
    dt = dt.astimezone(pytz.timezone("Asia/Shanghai"))
    return f"{util.month_name(dt.month)}{util.date_name(dt.day)}・{util.time_name(dt.hour, dt.minute)}"

def format_tweet(tweet):
    name = tweet.user.name
    time = format_time(tweet.created_at)
    text = tweet.text
    media = tweet.get('extended_entities', {}).get('media', [])
    imgs = ' '.join([str(ms.image(m.media_url)) for m in media])
    msg = f"@{name}\n{time}\n\n{text}"
    if imgs:
        msg = f"{msg}\n{imgs}"
    return msg


sv = Service("twitter-poller", use_priv=priv.SUPERUSER, manage_priv=priv.SUPERUSER, visible=False)
sv_kc = Service("kc-twitter", help_="艦これ推特转发", enable_on_default=False, bundle="kancolle")
sv_pcr = Service("pcr-twitter", help_="日服Twitter转发", enable_on_default=True, bundle="pcr订阅")
sv_uma = Service("uma-twitter", help_="ウマ娘推特转发", enable_on_default=False, bundle="umamusume")
sv_pripri = Service("pripri-twitter", help_="番剧《公主代理人》官推转发", enable_on_default=False)
sv_coffee_fav = Service("coffee-favorite-twitter", help_="咖啡精选画师推特转发", enable_on_default=False, bundle="artist")
sv_moe_artist = Service("moe-artist-twitter", help_="萌系画师推特转发", enable_on_default=False, bundle="artist")
sv_depress_artist = Service("depress-artist-twitter", help_="致郁系画师推特转发", enable_on_default=False, bundle="artist")
sv_test = Service("twitter-stream-test", enable_on_default=False, manage_priv=priv.SUPERUSER, visible=False)

router = TweetRouter()
router.add(sv_kc, ["KanColle_STAFF", "C2_STAFF", "ywwuyi", "FlatIsNice"])
router.add(sv_pcr, ["priconne_redive", "priconne_anime"])
router.add(sv_pripri, ["pripri_anime"])
router.add(sv_uma, ["uma_musu", "uma_musu_anime"])
router.add(sv_test, ["Ice9Coffee"])

coffee_fav = ["shiratamacaron", "k_yuizaki", "suzukitoto0323", "usagicandy_taku"]
moe_artist = ["koma_momozu", "santamatsuri", "panno_mimi", "suimya", "Anmi_", "mamgon", "kazukiadumi", "Setmen_uU"]
depress_artist = ["tkmiz"]
router.add(sv_coffee_fav, coffee_fav)
router.add(sv_moe_artist, moe_artist)
router.add(sv_depress_artist, depress_artist)
for i in [*moe_artist, *depress_artist]:
    router.set_media_only(i)


bot = hoshino.get_bot()

@bot.on_startup
async def start_daemon():
    loop = asyncio.get_event_loop()
    loop.create_task(twitter_stream_daemon())


async def twitter_stream_daemon():
    client = PeonyClient(consumer_key=cfg.consumer_key,
                         consumer_secret=cfg.consumer_secret,
                         access_token=cfg.access_token_key,
                         access_token_secret=cfg.access_token_secret)
    async with client:
        while True:
            try:
                await open_stream(client)
            except KeyboardInterrupt:
                return
            except Exception as e:
                sv.logger.exception(e)
                sv.logger.error(f"Error {type(e)} Occurred in twitter stream. Restarting stream.")


async def open_stream(client):
    sv.logger.debug("Opening twitter stream...")
    follow_ids = [(await client.api.users.show.get(screen_name=i)).id for i in router.follows]
    sv.logger.debug(f"{follow_ids=}")
    stream = client.stream.statuses.filter.post(follow=follow_ids)
    sv.logger.debug("stream created.")
    async with stream:
        sv.logger.debug("stream opened.")
        async for tweet in stream:
            sv.logger.debug("Got twitter event.")
            if peony.events.tweet(tweet):
                screen_name = tweet.user.screen_name
                media = tweet.get('extended_entities', {}).get('media', [])
                msg = format_tweet(tweet)

                if peony.events.retweet(tweet):
                    sv.logger.debug(f"获得转推：\n{msg}")
                    continue

                if 'quoted_status' in tweet:
                    sv.logger.info(f"获得引用：\n{msg}")
                    quoted_msg = format_tweet(tweet.quoted_status)
                    msg = f"{msg}\n\n>>>>>\n{quoted_msg}"

                if 'in_reply_to_status_id' in tweet and tweet.in_reply_to_status_id:
                    sv.logger.info(f"获得评论：\n{msg}")
                    continue

                if screen_name not in router.follows:
                    sv.logger.warning(f"推主 @{screen_name} 不在订阅列表!\n{msg}")
                    continue

                if router.follows[screen_name].media_only and not media:
                    continue

                sv.logger.info(f"推送推文：\n{msg}")
                for s in router.follows[screen_name].services:
                    await s.broadcast(msg, f' @{screen_name} 推文', 0.3)

            else:
                sv.logger.info("Ignore non-tweet event.")
