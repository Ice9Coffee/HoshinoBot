import re
from datetime import datetime

import peony
import pytz
from hoshino import util
from hoshino.typing import MessageSegment as ms


def format_time(time_str):
    dt = datetime.strptime(time_str, r'%Y-%m-%dT%H:%M:%S.%f%z')
    dt = dt.astimezone(pytz.timezone("Asia/Shanghai"))
    return f"{util.month_name(dt.month)}{util.date_name(dt.day)}・{util.time_name(dt.hour, dt.minute)}"


def format_tweet(tweet):
    name = tweet.get('includes')['users'][0]['name']
    # avatar = tweet.user.get("profile_image_url_https", "https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png")
    # avatar = re.sub(r'_normal(\.(jpg|jpeg|png|gif|jfif|webp))$', r'_200x200\1', avatar, re.I)

    if peony.events.retweet(tweet):
        return f"@{name} 转推了\n>>>>>\n{format_tweet(tweet.retweeted_status)}"
    time = format_time(tweet.get('data')['created_at'])
    text = tweet.get('data')['text']
    msg = f"@{name}\n{time}\n\n{text}"
    if 'media' in tweet.get('includes'):
        media= tweet.get('includes')['media']
        imgs = "".join([str(ms.image(m.url)) for m in media])
        msg = f"{msg}\n{imgs}"
    if "quoted_status" in tweet:
        quoted_msg = format_tweet(tweet.quoted_status)
        msg = f"{quoted_msg}\n\n<<<<<\n{msg}"

    return msg

def cut_list(lists, cut_len):
    """
    将列表拆分为指定长度的多个列表
    :param lists: 初始列表
    :param cut_len: 每个列表的长度
    :return: 一个二维数组 [[x,x],[x,x]]
    """
    res_data = []
    if len(lists) > cut_len:
        for i in range(int(len(lists) / cut_len)):
            cut_a = lists[cut_len * i:cut_len * (i + 1)]
            res_data.append(cut_a)

        last_data = lists[int(len(lists) / cut_len) * cut_len:]
        if last_data:
            res_data.append(last_data)
    else:
        res_data.append(lists)

    return res_data