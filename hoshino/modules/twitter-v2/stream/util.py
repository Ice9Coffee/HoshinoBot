from datetime import datetime

import pytz

from hoshino import util
from hoshino.typing import MessageSegment as ms

from . import sv


def format_time(time_str):
    dt = datetime.strptime(time_str, r"%Y-%m-%dT%H:%M:%S.%f%z")
    dt = dt.astimezone(pytz.timezone("Asia/Shanghai"))
    return f"{util.month_name(dt.month)}{util.date_name(dt.day)}・{util.time_name(dt.hour, dt.minute)}"


def is_retweet(tweet):
    data = tweet.get("data")
    if isinstance(data, list):
        data = data[0]
    if "referenced_tweets" not in data:
        return False
    return data["referenced_tweets"][0]["type"] == "retweeted"


def is_quote(tweet):
    data = tweet.get("data")
    if isinstance(data, list):
        data = data[0]
    if "referenced_tweets" not in data:
        return False
    return data["referenced_tweets"][0]["type"] == "quoted"


def is_reply(tweet):
    data = tweet.get("data")
    if isinstance(data, list):
        data = data[0]
    if "referenced_tweets" not in data:
        return False
    return data["referenced_tweets"][0]["type"] == "replied_to"


async def get_tweet(tweet_id, client):
    params = {
        "ids": tweet_id,
        "tweet.fields": [
            "created_at",
            "entities",
            "referenced_tweets",
            "text",
            "author_id",
            "in_reply_to_user_id",
            "attachments",
        ],
        "expansions": ["author_id", "attachments.media_keys"],  # 不要删media_keys，否则下行不生效
        "media.fields": ["url", "preview_image_url"],
    }
    resp = await client.api.tweets.get(**params)
    try:
        resp.data = resp.data[0]
    except KeyError:
        pass
    sv.logger.debug(type(resp))
    sv.logger.debug(type(resp.data))
    sv.logger.debug(resp)
    return resp

MAX_DEPTH = 1
async def format_tweet(tweet, client, quote_depth=0):
    name = tweet.get("includes")["users"][0]["name"]
    try:
        data = tweet.get("data")[0]
    except KeyError:
        data = tweet.get("data")

    if quote_depth < MAX_DEPTH and is_retweet(tweet):
        retweeted_tweet = await get_tweet(data["referenced_tweets"][0]["id"], client)
        retweeted_msg = await format_tweet(retweeted_tweet, client, quote_depth + 1)
        return f"@{name} 转推了\n>>>>>\n{retweeted_msg}"

    time = format_time(data["created_at"])
    text = data["text"]
    msg = f"@{name}\n{time}\n\n{text}"

    if "media" in tweet.get("includes"):
        media = tweet.get("includes")["media"]
        imgs = "".join([str(ms.image(m.url)) for m in media])
        msg = f"{msg}\n{imgs}"

    if quote_depth < MAX_DEPTH and (is_quote(tweet) or is_reply(tweet)):
        quoted_tweet = await get_tweet(data["referenced_tweets"][0]["id"], client)
        quoted_msg = await format_tweet(quoted_tweet, client, quote_depth + 1)
        msg = f"{quoted_msg}\n\n<<<<<\n{msg}"

    return msg


def cut_list(lists):
    """
    将关注列表拆分为不超过512字节的多个列表
    :param lists: 初始列表
    :return: 一个二维数组 [[x,x],[x,x]]
    """
    res_data = [[]]
    length = -4                     # 5 - 9 = -4

    for x in lists:
        length += len(x) + 9        # len(' OR from:') = 9
        if length > 512:
            length = len(x) + 5     # len('from:') = 5
            res_data.append([])
        res_data[-1].append(x)

    if len(res_data) > 5:
        sv.logger.warning("关键词列表过长！Twitter API限制只能添加5个rule")
    return res_data
