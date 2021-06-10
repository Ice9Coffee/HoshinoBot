import re
import random
import json
import os
import datetime
import requests
from io import BytesIO
from random import choice
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from hoshino import R, Service, priv
from hoshino.typing import CQEvent, MessageSegment
from hoshino.util import pic2b64, FreqLimiter

sv_help = '''
生成器s:
[营销号 主体/事件/另一种说法] 营销号生成器
[狗屁不通 主题] 狗屁不通生成器
[记仇 天气/主题] 记仇表情包生成器
[我朋友说他好了] 无中生友，无艾特时随机群员
[日记 天气/主题] 舔狗日记生成器
'''.strip()

sv = Service(
    name='生成器',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # False隐藏
    enable_on_default=True,  # 是否默认启用
    bundle='娱乐',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助-生成器"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


_flmt = FreqLimiter(300)


def load_config(path):
    try:
        with open(path, 'r', encoding='utf8') as f:
            config = json.load(f)
            return config
    except:
        return {}


def measure(msg, font_size, img_width):
    i = 0
    l = len(msg)
    length = 0
    positions = []
    while i < l:
        if re.search(r'[0-9a-zA-Z]', msg[i]):
            length += font_size // 2
        else:
            length += font_size
        if length >= img_width:
            positions.append(i)
            length = 0
            i -= 1
        i += 1
    return positions


def get_pic(qq):
    apiPath = f'http://q1.qlogo.cn/g?b=qq&nk={qq}&s=100'
    return requests.get(apiPath, timeout=20).content


def get_name(qq):
    url = 'http://r.qzone.qq.com/fcg-bin/cgi_get_portrait.fcg'
    params = {'uins': qq}
    res = requests.get(url, params=params)
    res.encoding = 'GBK'
    data_match = re.search(r'\((?P<data>[^\(\)]*)\)', res.text)
    if data_match:
        j_str = data_match.group('data')
        return json.loads(j_str)[qq][-2]
    else:
        return '富婆'


@sv.on_prefix('营销号')
async def yxh(bot, ev: CQEvent):
    kw = ev.message.extract_plain_text().strip()
    arr = kw.split('/')
    msg = f'    {arr[0]}{arr[1]}是怎么回事呢？{arr[0]}相信大家都很熟悉，但是{arr[0]}{arr[1]}是怎么回事呢，下面就让小编带大家一起了解吧。\n    {arr[0]}{arr[1]}，其实就是{arr[2]}，大家可能会很惊讶{arr[0]}怎么会{arr[1]}呢？但事实就是这样，小编也感到非常惊讶。\n    这就是关于{arr[0]}{arr[1]}的事情了，大家有什么想法呢，欢迎在评论区告诉小编一起讨论哦！'
    await bot.send(ev, msg)


@sv.on_prefix('狗屁不通')
async def gpbt(bot, ev: CQEvent):
    data = load_config(os.path.join(os.path.dirname(__file__), 'data.json'))
    title = ev.message.extract_plain_text().strip()
    length = 500
    body = ""
    while len(body) < length:
        num = random.randint(0, 100)
        if num < 10:
            body += "\r\n"
        elif num < 20:
            body += random.choice(data["famous"]) \
                .replace('a', random.choice(data["before"])) \
                .replace('b', random.choice(data['after']))
        else:
            body += random.choice(data["bosh"])
        body = body.replace("x", title)
    await bot.send(ev, body)


@sv.on_prefix('记仇')
async def jc(bot, ev: CQEvent):
    kw = ev.message.extract_plain_text().strip()
    arr = kw.split('/')
    image = Image.open(os.path.join(os.path.dirname(__file__), 'jichou.jpg'))
    # 创建Font对象:
    font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'simhei.ttf'), 80)

    time = datetime.datetime.now().strftime('%Y年%m月%d日')
    msg = f'{time}，{arr[0]}，{arr[1]}，这个仇我先记下了'
    place = 12
    line = len(msg.encode('utf-8')) // place + 1

    positions = measure(msg, 80, 974)
    str_list = list(msg)
    for pos in positions:
        str_list.insert(pos, '\n')
    msg = "".join(str_list)
    # 创建Draw对象:
    image_text = Image.new('RGB', (974, 32 * line), (255, 255, 255))
    draw = ImageDraw.Draw(image_text)
    draw.text((0, 0), msg, fill=(0, 0, 0), font=font)
    # 模糊:
    image_text = image_text.filter(ImageFilter.BLUR)
    image_back = Image.new('RGB', (974, 32 * line + 764), (255, 255, 255))
    image_back.paste(image, (0, 0))
    image_back.paste(image_text, (0, 764))

    await bot.send(ev, str(MessageSegment.image(pic2b64(image_back))))


@sv.on_rex('^我(有个|一个|有一个)*朋友(想问问|说|让我问问|想问|让我问|想知道|让我帮他问问|让我帮他问|让我帮忙问|让我帮忙问问|问)*(?P<kw>.{0,30}$)')
async def friend(bot, ev: CQEvent):
    # 定义非管理员的冷却时间
    # if ev.user_id not in bot.config.SUPERUSERS:
    #     if not _flmt.check(ev.user_id):
    #         return
    # _flmt.start_cd(ev.user_id)
    data = load_config(os.path.join(os.path.dirname(__file__), 'config.json'))['friend']
    arr = []
    is_at = False
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            arr = [int(m.data['qq'])]
            sid = int(m.data['qq'])
            is_at = True
    if not is_at:
        try:
            arr = data[f'{ev.group_id}']
        except:
            member_list = await bot.get_group_member_list(self_id=ev.self_id, group_id=ev.group_id)
            for member in member_list:
                arr.append(member['user_id'])
            sid = choice(arr)
    info = await bot.get_group_member_info(
        group_id=ev.group_id,
        user_id=sid,
        no_cache=True
    )
    name = info['card'] or info['nickname']
    match = ev['match']
    msg = match.group('kw')
    msg = msg.replace('他', '我').replace('她', '我')
    image = Image.open(BytesIO(get_pic(sid)))
    img_origin = Image.new('RGBA', (100, 100), (255, 255, 255))
    scale = 3
    # 使用新的半径构建alpha层
    r = 100 * scale
    alpha_layer = Image.new('L', (r, r), 0)
    draw = ImageDraw.Draw(alpha_layer)
    draw.ellipse((0, 0, r, r), fill=255)
    # 使用ANTIALIAS采样器缩小图像
    alpha_layer = alpha_layer.resize((100, 100), Image.ANTIALIAS)
    img_origin.paste(image, (0, 0), alpha_layer)

    # 创建Font对象:
    font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'simhei.ttf'), 30)
    font2 = ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'simhei.ttf'), 25)

    # 创建Draw对象:
    image_text = Image.new('RGB', (450, 150), (255, 255, 255))
    draw = ImageDraw.Draw(image_text)
    draw.text((0, 0), name, fill=(0, 0, 0), font=font)
    draw.text((0, 40), msg, fill=(125, 125, 125), font=font2)

    image_back = Image.new('RGB', (700, 150), (255, 255, 255))
    image_back.paste(img_origin, (25, 25))
    image_back.paste(image_text, (150, 40))

    await bot.send(ev, str(MessageSegment.image(pic2b64(image_back))))


pre = 0


@sv.on_rex('日记')
async def diary(bot, ev: CQEvent):
    global pre
    name = '富婆'
    for i in ev.message:
        if i.get('type', False) == 'at':
            name = get_name(i.data['qq'])

    kw = ev.message.extract_plain_text().strip()
    time = datetime.datetime.now().strftime('%Y年%m月%d日')
    arr = kw.split('/')
    content = ''
    if len(arr) >= 2:
        weather, content = arr
        weather = weather.split(' ')[-1]
    else:
        weather = ''
        if arr[0].split(' ') == 2:
            weather = arr[0].split(' ')[-1]

    if not content:
        with open(os.path.join(os.path.dirname(__file__), 'diary_data.json'), 'r', encoding='utf-8') as file:
            diaries = json.load(file)
            while True:
                index = random.randint(0, len(diaries) - 1)
                if index != pre:
                    pre = index
                    content = diaries[index]
                    for s in '你她':
                        content = content.replace(s, name)
                    break

    image = Image.open(os.path.join(os.path.dirname(__file__), 'diary.png'))
    img_width, img_height = image.size
    # 创建Font对象:
    font_size = img_width // 18
    font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'simhei.ttf'), font_size)
    positions = measure(content, font_size, img_width)
    str_list = list(content)
    for pos in positions:
        str_list.insert(pos, '\n')
    # 日期单独一行
    line = len(positions) + 2
    content = f'{time}，{weather}\n' + "".join(str_list)
    line_h = font_size + 4
    # 创建Draw对象:
    image_text = Image.new('RGB', (img_width, line_h * line), (255, 255, 255))
    draw = ImageDraw.Draw(image_text)
    draw.text((0, 0), content, fill=(0, 0, 0), font=font, spacing=2)
    # 模糊:
    # image_text = image_text.filter(ImageFilter.BLUR)
    image_back = Image.new('RGB', (img_width, line_h * line + img_height), (255, 255, 255))
    image_back.paste(image, (0, 0))
    image_back.paste(image_text, (0, img_height))

    await bot.send(ev, str(MessageSegment.image(pic2b64(image_back))))
