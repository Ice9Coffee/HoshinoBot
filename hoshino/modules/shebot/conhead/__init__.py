import base64
import pickle
import os
import time
from io import BytesIO
from os import path

import aiohttp
from PIL import Image

from .._res import Res as R
from hoshino.service import Service, priv
from hoshino.typing import HoshinoBot, CQEvent
from hoshino.util import DailyNumberLimiter, FreqLimiter
from .._util import extract_url_from_event
from .data_source import detect_face, concat, gen_head
from .opencv import add
from .config import *

sv_help = """"""

sv = Service(
    name='接头霸王',
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 是否可见
    enable_on_default=True,  # 是否默认启用
    bundle='订阅',  # 属于哪一类
    help_=sv_help  # 帮助文本
)
_nlt = DailyNumberLimiter(5)
_flt = FreqLimiter(15)


@sv.on_prefix(('接头霸王', '接头'))
async def concat_head(bot: HoshinoBot, ev: CQEvent):
    uid = ev.user_id
    if not _nlt.check(uid):
        await bot.finish(ev, '今日已经到达上限！')

    if not _flt.check(uid):
        await bot.finish(ev, '太频繁了，请稍后再来')

    url = extract_url_from_event(ev)
    if not url:
        await bot.finish(ev, '请附带图片!')
    url = url[0]
    await bot.send(ev, '请稍等片刻~')

    _nlt.increase(uid)
    _flt.start_cd(uid, 30)

    # download picture and generate base64 str
    # b百度人脸识别api好像无法使用QQ图片服务器的图片，所以使用base64
    async with  aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            cont = await resp.read()
            b64 = (base64.b64encode(cont)).decode()
            img = Image.open(BytesIO(cont))
            img.save(path.join(path.dirname(__file__), 'temp.jpg'))
            picfile = path.join(path.dirname(__file__), 'temp.jpg')
    print('raw message: ', ev.raw_message)
    if str(ev.message[0]).startswith('1'):
        mode = 1
    elif str(ev.message[0]).startswith('2'):
        mode = 2
    else:
        mode = DEFAULT_MODE
    if mode == 1:  # 使用百度api接头
        if not CLIENT_ID or not CLIENT_SECRET:
            await bot.finish(ev, '请配置client_id和client_secret')
        face_data_list = await detect_face(b64)
        if not face_data_list:
            await bot.finish(ev, 'api未检测到人脸信息')
        face_data_list = await detect_face(b64)
        output = ''  ######
        head_gener = gen_head()
        for dat in face_data_list:
            try:
                head = head_gener.__next__()
            except StopIteration:
                head_gener = gen_head()
                head = head_gener.__next__()
            output = concat(img, head, dat)
        pic = R.image_from_memory(output)
        await bot.send(ev, pic)
    else:  # 使用opencv
        picname = time.strftime("%F-%H%M%S") + ".png"
        outpath = path.join(path.dirname(__file__), 'output', picname)
        if add(picfile, outpath):
            await bot.send(ev, R.image(outpath))
        else:
            fail_pic = path.join(path.dirname(__file__), 'data', '接头失败.png')
            await bot.send(ev, R.image(fail_pic))
