from nonebot import MessageSegment
import os
import asyncio
import time
import json
import traceback
import nonebot
import random
import threading
import re
import string
from hashlib import md5
from time import time
from urllib.parse import quote_plus
import hoshino
import aiohttp
from nonebot import get_bot
from nonebot.helpers import render_expression
from hoshino import Service, priv

# from hoshino.service import Service, Privilege as Priv
try:
    import ujson as json
except ImportError:
    import json

sv_help = '''
[@bot XX] @bot就可以与bot对话
'''.strip()

sv = Service(
    name='人工智障',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # False隐藏
    enable_on_default=True,  # 是否默认启用
    bundle='通用',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助-人工智障"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


bot = get_bot()
cq_code_pattern = re.compile(r'\[CQ:\w+,.+\]')
salt = None

# 定义无法获取回复时的「表达（Expression）」
EXPR_DONT_UNDERSTAND = (
    '我现在还不太明白你在说什么呢，但没关系，以后的我会变得更强呢！',
    '我有点看不懂你的意思呀，可以跟我聊些简单的话题嘛',
    '其实我不太明白你的意思……',
    '抱歉哦，我现在的能力还不能够明白你在说什么，但我会加油的～',
    '唔……等会再告诉你'
)

################
# 请修改
app_id = hoshino.config.tenxun_api_ID
app_key = hoshino.config.tenxun_api_KEY


################

def getReqSign(params: dict) -> str:
    hashed_str = ''
    for key in sorted(params):
        hashed_str += key + '=' + quote_plus(params[key]) + '&'
    hashed_str += 'app_key=' + app_key
    sign = md5(hashed_str.encode())
    return sign.hexdigest().upper()


def rand_string(n=8):
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(n))


@sv.on_message('group')
async def ai_reply(bot, context):
    msg = str(context['message'])

    if not msg.startswith(f'[CQ:at,qq={context["self_id"]}]'):
        return

    text = re.sub(cq_code_pattern, '', msg).strip()
    if text == '':
        return

    global salt
    if salt is None:
        salt = rand_string()
    session_id = md5((str(context['user_id']) + salt).encode()).hexdigest()

    param = {
        'app_id': app_id,
        'session': session_id,
        'question': text,
        'time_stamp': str(int(time())),
        'nonce_str': rand_string(),
    }
    sign = getReqSign(param)
    param['sign'] = sign

    async with aiohttp.request(
            'POST',
            'https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat',
            params=param,
    ) as response:
        code = response.status
        if code != 200:
            raise ValueError(f'bad server http code: {code}')
        res = await response.read()
        # print (res)
    param = json.loads(res)
    if param['ret'] != 0:
        raise ValueError(param['msg'])
    reply = param['data']['answer']
    if reply:
        await bot.send(context, reply, at_sender=False)
    else:
        # 如果调用失败，或者它返回的内容我们目前处理不了，发送无法获取回复时的「表达」
        # 这里的 render_expression() 函数会将一个「表达」渲染成一个字符串消息
        await bot.send(render_expression(EXPR_DONT_UNDERSTAND))
