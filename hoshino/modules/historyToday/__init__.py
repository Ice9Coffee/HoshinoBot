import urllib
import requests
import json
import urllib.request
from bs4 import BeautifulSoup
import pytz
import re
from datetime import datetime, timedelta
from hoshino import Service
from hoshino.typing import CQEvent, MessageSegment

sv = Service('history', enable_on_default=True, help_='''历史上的今天''')


@sv.on_fullmatch(['历史上的今天', '看看历史'])
async def today_lishi(bot, ev: CQEvent):
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    nowyear = now.year
    nowmonth = now.month
    nowday = now.day
    if len(str(nowmonth)) == 1:
        monthnow = "0" + str(nowmonth)
    else:
        monthnow = str(nowmonth)

    if len(str(nowday)) == 1:
        daynow = "0" + str(nowday)
    else:
        daynow = str(nowday)

    today = monthnow + daynow

    # print(str(today))
    url = "https://baike.baidu.com/cms/home/eventsOnHistory/" + str(monthnow) + ".json"
    resp = urllib.request.urlopen(url)
    ele_json = json.loads(resp.read())
    msg = f"{str(nowyear)}年{monthnow}月{daynow}日\n"
    for items in ele_json[monthnow][today]:
        year = str(items['year'])
        pattern = re.compile(r'<[^>]+>', re.S)
        content = pattern.sub('', str(items['title']))
        # content = re.sub("[a-zA-Z0-9'!#$%&\'\"()*+,-./:;<=>?@，。?★、…【】《》？“”‘'！[\\]^_`{|}~\s]+", "", str(items['title']))
        msg = msg + f"{year}：{content}\n"
        # print(year)
        # print(title)
    await bot.send(ev, msg)
