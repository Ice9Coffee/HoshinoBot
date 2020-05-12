import os
import time
import pytz
import base64
import zhconv
import unicodedata
from io import BytesIO
from PIL import Image
from collections import defaultdict
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
try:
    import ujson as json
except:
    import json

from nonebot import get_bot
from aiocqhttp.exceptions import ActionFailed

from .log import logger


def load_config(inbuilt_file_var):
    """
    Just use `config = load_config(__file__)`,
    you can get the config.json as a dict.
    """
    filename = os.path.join(os.path.dirname(inbuilt_file_var), 'config.json')
    try:
        with open(filename, encoding='utf8') as f:
            config = json.load(f)
            return config
    except Exception as e:
        logger.exception(e)
        return {}


async def delete_msg(ctx):
    try:
        if get_bot().config.IS_CQPRO:
            msg_id = ctx['message_id']
            await get_bot().delete_msg(self_id=ctx['self_id'], message_id=msg_id)
    except ActionFailed as e:
        logger.error(f'撤回失败 retcode={e.retcode}')
    except Exception as e:
        logger.exception(e)


async def silence(ctx, ban_time, ignore_super_user=False):
    try:
        self_id = ctx['self_id']
        group_id = ctx['group_id']
        user_id = ctx['user_id']
        bot = get_bot()
        if ignore_super_user or user_id not in bot.config.SUPERUSERS:
            await bot.set_group_ban(self_id=self_id, group_id=group_id, user_id=user_id, duration=ban_time)
    except ActionFailed as e:
        logger.error(f'禁言失败 retcode={e.retcode}')
    except Exception as e:
        logger.exception(e)


def checkBase64Length(base64_len):
    return base64_len * 0.75 < 4000000

def resize_4m(img: Image, b64_len):
    b64_len *= 0.75
    if b64_len < 4000000:
        return img
    scale = b64_len / 4000000
    w, h = img.size
    img.thumbnail((int(w / scale), int(h / scale)), Image.ANTIALIAS)
    return img

def pic2b64(pic: Image) -> str:
    buf = BytesIO()
    pic.save(buf, format='PNG')
    base64_str = base64.b64encode(buf.getvalue()).decode()   #, encoding='utf8')
    b64_len = len(base64_str)
    if not checkBase64Length(b64_len):
        return pic2b64(resize_4m(pic, b64_len))
    return 'base64://' + base64_str


def fig2b64(plt:plt) -> str:
    buf = BytesIO()
    plt.savefig(buf, format='PNG', dpi=100)
    base64_str = base64.b64encode(buf.getvalue()).decode()
    return 'base64://' + base64_str


def concat_pic(pics, border=5):
    num = len(pics)
    w, h = pics[0].size
    des = Image.new('RGBA', (w, num * h + (num-1) * border), (255, 255, 255, 255))
    for i, pic in enumerate(pics):
        des.paste(pic, (0, i * (h + border)), pic)
    return des


def normalize_str(string) -> str:
    """
    规范化unicode字符串 并 转为小写 并 转为简体
    """
    string = unicodedata.normalize('NFKC', string)
    string = string.lower()
    string = zhconv.convert(string, 'zh-hans')
    return string


MONTH_NAME = ('睦月', '如月', '弥生', '卯月', '皐月', '水無月'
              '文月', '葉月', '長月', '神無月', '霜月', '師走')
def month_name(x:int) -> str:
    return MONTH_NAME[x - 1]

DATE_NAME = (
    '初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
    '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
    '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十',
    '卅一'
)
def date_name(x:int) -> str:
    return DATE_NAME[x - 1]

NUM_NAME = (
    '〇〇', '〇一', '〇二', '〇三', '〇四', '〇五', '〇六', '〇七', '〇八', '〇九',
    '一〇', '一一', '一二', '一三', '一四', '一五', '一六', '一七', '一八', '一九', 
    '二〇', '二一', '二二', '二三', '二四', '二五', '二六', '二七', '二八', '二九', 
    '三〇', '三一', '三二', '三三', '三四', '三五', '三六', '三七', '三八', '三九', 
    '四〇', '四一', '四二', '四三', '四四', '四五', '四六', '四七', '四八', '四九', 
    '五〇', '五一', '五二', '五三', '五四', '五五', '五六', '五七', '五八', '五九',
    '六〇', '六一', '六二', '六三', '六四', '六五', '六六', '六七', '六八', '六九', 
    '七〇', '七一', '七二', '七三', '七四', '七五', '七六', '七七', '七八', '七九', 
    '八〇', '八一', '八二', '八三', '八四', '八五', '八六', '八七', '八八', '八九', 
    '九〇', '九一', '九二', '九三', '九四', '九五', '九六', '九七', '九八', '九九',
)
def time_name(hh:int, mm:int) -> str:
    return NUM_NAME[hh] + NUM_NAME[mm]


class FreqLimiter:
    def __init__(self, default_cd_seconds):
        self.next_time = defaultdict(float)
        self.default_cd = default_cd_seconds

    def check(self, key) -> bool:
        return bool(time.time() >= self.next_time[key])

    def start_cd(self, key, cd_time=0):
        self.next_time[key] = time.time() + cd_time if cd_time > 0 else self.default_cd


class DailyNumberLimiter:
    tz = pytz.timezone('Asia/Shanghai')
    
    def __init__(self, max_num):
        self.today = -1
        self.count = defaultdict(int)
        self.max = max_num

    def check(self, key) -> bool:
        now = datetime.now(self.tz)
        day = (now - timedelta(hours=5)).day
        if day != self.today:
            self.today = day
            self.count.clear()
        return bool(self.count[key] < self.max)

    def get_num(self, key):
        return self.count[key]

    def increase(self, key, num=1):
        self.count[key] += num

    def reset(self, key):
        self.count[key] = 0
