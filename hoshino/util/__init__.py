import base64
import os
import random
import time
import unicodedata
from collections import defaultdict
from datetime import datetime, timedelta
from io import BytesIO

import pytz
import zhconv
from aiocqhttp.exceptions import ActionFailed
from aiocqhttp.message import escape
from matplotlib import pyplot as plt
from PIL import Image

import hoshino
from hoshino.typing import CQEvent, Message, Union

try:
    import ujson as json
except:
    import json




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
        hoshino.logger.exception(e)
        return {}


async def delete_msg(ev: CQEvent):
    try:
        await hoshino.get_bot().delete_msg(self_id=ev.self_id, message_id=ev.message_id)
    except ActionFailed as e:
        hoshino.logger.error(f'撤回失败: {e}')
    except Exception as e:
        hoshino.logger.exception(e)


async def silence(ev: CQEvent, ban_time, skip_su=True):
    try:
        if skip_su and ev.user_id in hoshino.config.SUPERUSERS:
            return
        await hoshino.get_bot().set_group_ban(self_id=ev.self_id, group_id=ev.group_id, user_id=ev.user_id, duration=ban_time)
    except ActionFailed as e:
        if 'NOT_MANAGEABLE' in str(e):
            return
        else:
            hoshino.logger.error(f'禁言失败 {e}')
    except Exception as e:
        hoshino.logger.exception(e)


def pic2b64(pic: Image) -> str:
    buf = BytesIO()
    pic.save(buf, format='PNG')
    base64_str = base64.b64encode(buf.getvalue()).decode()
    return 'base64://' + base64_str


def fig2b64(plt: plt) -> str:
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


MONTH_NAME = ('睦月', '如月', '弥生', '卯月', '皐月', '水無月',
              '文月', '葉月', '長月', '神無月', '霜月', '師走')
def month_name(x:int) -> str:
    return MONTH_NAME[x - 1]

DATE_NAME = (
    '初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
    '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
    '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十',
    '卅一'
)
def date_name(x: int) -> str:
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
def time_name(hh: int, mm: int) -> str:
    return NUM_NAME[hh] + NUM_NAME[mm]


class FreqLimiter:
    def __init__(self, default_cd_seconds):
        self.next_time = defaultdict(float)
        self.default_cd = default_cd_seconds

    def check(self, key) -> bool:
        return bool(time.time() >= self.next_time[key])

    def start_cd(self, key, cd_time=0):
        self.next_time[key] = time.time() + (cd_time if cd_time > 0 else self.default_cd)

    def left_time(self, key) -> float:
        return self.next_time[key] - time.time()


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


from .textfilter.filter import DFAFilter

gfw = DFAFilter()
gfw.parse(os.path.join(os.path.dirname(__file__), 'textfilter/sensitive_words.txt'))


def filt_message(message: Union[Message, str]):
    if isinstance(message, str):
        return gfw.filter(message)
    elif isinstance(message, Message):
        for seg in message:
            if seg.type == 'text':
                seg.data['text'] = gfw.filter(seg.data.get('text', ''))
        return message
    else:
        raise TypeError



def render_list(lines, prompt="") -> str:
    n = len(lines)
    if n == 0:
        return prompt
    if n == 1:
        return prompt + "\n┗" + lines[0]
    return prompt + "\n┣" + "\n┣".join(lines[:-1]) + "\n┗" + lines[-1]


# DEVICES = [
#     '22号对水上电探改四(后期调整型)',
#     '42号对空电探改二',
#     '15m二重测距仪改+21号电探改二+熟练射击指挥所',
#     'FuMO25 雷达',
#     'SK+SG 雷达',
#     'SG 雷达(后期型)',
#     'GFCS Mk.37',
#     '潜水舰搭载电探&逆探(E27)',
#     'HF/DF+Type144/147 ASDIC',
#     '三式指挥联络机(对潜)',
#     'O号观测机改二',
#     'S-51J改',
#     '二式陆上侦察机(熟练)',
#     '东海(九〇一空)',
#     '二式大艇',
#     'PBY-5A Catalina',
#     '零式水上侦察机11型乙(熟练)',
#     '零式水上侦察机11型乙改(夜侦)',
#     '紫云',
#     'Ar196改',
#     'Ro.43水侦',
#     'OS2U',
#     'S9 Osprey',
#     '彩云(东加罗林空)',
#     '彩云(侦四)',
#     '试制景云(舰侦型)',
# ]


DEVICES = [
    # 芳文社
    # Kirara Fantasia
    '由乃', '宫子', '寻', '沙英', '乃莉', '荠',  # 向阳素描
    '野野原柚子', '栎井唯', '日向缘', '松本赖子', '相川千穗', '冈野佳', '长谷川文',  # YUYU式
    '丈枪由纪', '惠飞须泽胡桃', '若狭悠里', '直树美纪', '佐仓慈', '祠堂圭',  # 学园孤岛
    '一井透', '百木伦', '西由宇子', '天王寺渚', '野山美步', '今井丰', '鬼头纪美子',  # A Channel
    '九条可怜', '爱丽丝·卡塔雷特', '大宫忍', '小路绫', '猪熊阳子', '松原穗乃花', '大宫勇', '乌丸樱', '久世桥朱里', '日暮香奈',  # 黄金拼图
    '凉风青叶', '泷本一二三', '篠田初', '饭岛结音', '八神光', '远山伦', '樱宁宁', '阿波根海子', '望月红叶', '鸣海燕', '叶月雫', '星川萤',  # NEW GAME!
    '本田珠辉', '藤川歌夜', '村上椎奈', '关菖蒲', '布田裕美音', '百武照', '饭野水叶', '池谷乃乃', '鹤濑茉莉',  # 斯特拉的魔法
    '千矢', '巽绀', '雪见小梅', '枣乃乃', '色井佐久', '枣妮娜', '二条臣', '花原椿', '玛丽·琪斯皮尔库艾特',  # Urara迷路帖
    '折部安奈', '索妮娅', '吴织亚切',  # 爱杀宝贝
    '高山春香', '园田优', '南雫', '野田琴音', '池野枫', '饭冢柚', '乙川澄', '园田美月',  # 樱Trick
    '樱之宫莓香', '日向夏帆', '星川麻冬', '天野美雨', '神崎日照', '樱之宫爱香',  # Blend·S
    '一之濑花名', '千石冠', '十仓荣依子', '百地玉手', '万年大会', '京冢志温', '榎并清濑', '十仓光希',  # Slow Start
    '平泽唯', '秋山澪', '田井中律', '琴吹䌷', '中野梓', '平泽忧', '山中佐和子',  # 轻音少女
    '志摩凛', '各务原抚子', '大垣千明', '犬山葵', '齐藤惠那', '土岐绫乃',  # 摇曳露营△
    '萌田薰子', '恋冢小梦', '色川琉姬', '胜木翼', '怖浦铃', '色川美姬', '虹野美晴', '编泽麻友',  # Comic Girls
    '山口如月', '野田美希', '友兼', '大道雅', '野崎奈三子',  # GA 艺术科美术设计班
    '玛莉·梦魔', '橘勇鱼', '安琪·三叶', '光凪由衣', '克里奥奈',  # 食梦者玛莉
    '关谷鸣', '哈娜·N·芳婷史坦', '笹目夜弥', '西御门多美', '常盘真智',  # 花舞少女
    '花小泉杏', '云雀丘琉璃', '久米川牡丹', '萩生响', '江古田莲', '狭山椿',  # Anne Happy
    '大空遥', '比嘉彼方', '托马斯·红爱', '托马斯·惠美理', '大城明', '远井成美', '立花彩纱',  # 遥的接球
    '保登心爱', '香风智乃', '天天座理世', '宇治松千夜', '桐间纱路', '条河麻耶', '奈津惠', '保登摩卡', '青山翠',  # 请问您今天要来点兔子吗？
    '鸠谷小羽', '有马日诘', '猿渡宇希', '馆岛虎彻', '牛久花和', '稻叶兔和',  # Anima Yell!
    '西川叶子', '小田切双叶', '叶山照', '西山芹奈', '园部篠', '近藤亚纱子', '叶山光',  # 三者三叶
    '小黑',  # 棺材、旅人、怪蝙蝠
    '吉田优子', '千代田桃', '莉莉丝', '阳夏木蜜柑', '吉田良子',  # 街角魔族
    '细野晴海', '坂本香树', '高桥雪', '细野步海',  # 晴海国度
    '町子凉', '森野麒麟', '椎名', '内木由纪',  # 幸腹涂鸦
    '木之幡米拉', '真中苍', '猪濑舞', '樱井美景', '森野真理',  # 恋爱小行星
    '武田咏深', '山崎珠姬', '川口芳乃', '中村希',  # 球咏
    '樱衣乃', '关野露子', '贯井羽优', '前原仁菜', '绿黑萌',  # 满溢的水果挞
    '御庭摘希', '春野姬', '片濑真宵', '樱川菊绘',  # 一起一起这里那里
    '篠华茉优', '虎道环', '丛园寺观久',  # 倾心一抹笑
    '小野坂小春', '橘妮娜', '北泽岬', '牧之濑日莉', '小野坂纱织',  # 小春日和。
    '里中千惠', '白井丽子',  # 房东妹子青春期！
    '仓桥莉子', '真木夏绪',  # 恋爱研究所
    '小森朱里', '西鸟惠', '根岸真子',  # 小森拒不了！
    '风色琴音', '弗雅', '露芙莉娅', '拉琪拉',  # RPG不动产
    '后藤一里', '伊地知虹夏', '山田凉', '喜多郁代',  # 孤独摇滚！
    '海凪日和', '海凪小春', '吉永恋',  # Slow Loop
]


def randomizer(target):
    return lambda m: f'{random.choice(DEVICES)}监测到{target}!{"!"*random.randint(0,4)}\n{m}'
