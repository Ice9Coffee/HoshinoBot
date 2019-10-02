import os
import logging
import base64

from io import BytesIO
from PIL import Image
from urllib.parse import urljoin, quote

from typing import List

from nonebot import on_command, CommandSession, MessageSegment
from aiocqhttp.exceptions import ActionFailed
from ._priconne_data import _PriconneData

USE_PRO_VERSION = True      # 是否使用酷Q PRO版功能，如撤回、发图等

IMG_BED = 'http://andong.ml/static/img/'    # 填写自己的图床地址

LOCAL_IMG_DIR = os.path.expanduser('~/mywebsite/static/img/priconne/')




async def delete_msg(session:CommandSession):
    try:
        if USE_PRO_VERSION:
            msg_id = session.ctx['message_id']
            await session.bot.delete_msg(message_id=msg_id)
    except ActionFailed as e:
        print('retcode=', e.retcode, ' 撤回消息需要酷Q Pro版以及管理员权限')


async def silence(session:CommandSession, ban_time):
    group_id = session.ctx['group_id']
    user_id = session.ctx['user_id']
    await session.bot.set_group_ban(group_id=group_id, user_id=user_id, duration=ban_time)


def get_cqimg(filename, path='', img_bed=IMG_BED):
    print('img_bed=', img_bed)
    print('path=', path)
    print('filename=', filename)
    url = urljoin(img_bed, path) + '/'
    url = urljoin(url, quote(filename))
    print('cqimg url=', url)
    return str(MessageSegment.image(url))


class CharaHelper(object):

    UNKNOWN_CHARA = 1000
    NAME2ID = {}

    @staticmethod
    def __gen_name2id():
        CharaHelper.NAME2ID = {}
        for k,v in _PriconneData.CHARA.items():
            for s in v:
                if s not in CharaHelper.NAME2ID:
                    CharaHelper.NAME2ID[s] = k
                else:
                    logging.getLogger('priconne.plugins.util.CharaHelper.__gen_name2id()').error(
                        f'出现重名{s}于id{k}与id{CharaHelper.NAME2ID[s]}'
                    )
        pass


    @staticmethod
    def get_name(id_) -> str:
        return _PriconneData.CHARA[id_][0] if id_ in _PriconneData.CHARA else None


    @staticmethod
    def get_id(name) -> int:
        if not CharaHelper.NAME2ID:
            CharaHelper.__gen_name2id()
        return CharaHelper.NAME2ID[name] if name in CharaHelper.NAME2ID else CharaHelper.UNKNOWN_CHARA


    @staticmethod
    def get_picname(id_) -> str:
        pic_pre = 'icon_unit_'
        pic_end = '31.png'
        if not 1000 < id_ < 2000:
            id_ = CharaHelper.UNKNOWN_CHARA      # unknown character
        return f'{pic_pre}{id_:0>4d}{pic_end}'


    @staticmethod
    def name2pic(name:str) -> str:
        id_ = CharaHelper.get_id(name)
        if not 1000 < id_ < 2000:
            id_ = CharaHelper.UNKNOWN_CHARA      # unknown character
        return CharaHelper.get_picname(id_)


    @staticmethod
    def gen_pic_base64(ids, size=128):
        pic = CharaHelper.gen_team_pic(ids, size)
        return CharaHelper.pic2b64(pic)


    @staticmethod
    def gen_team_pic(ids, size=128):
        num = len(ids)
        des = Image.new('RGBA', (num*size, size))
        for i, id_ in enumerate(ids):
            path = os.path.join(LOCAL_IMG_DIR, CharaHelper.get_picname(id_))
            src = Image.open(path).resize((size, size), Image.LANCZOS)
            des.paste(src, (i * size, 0))
        return des


    @staticmethod
    def concat_team_pic(pics):
        num = len(pics)
        w, h = pics[0].size
        des = Image.new('RGBA', (w, num * h))
        for i, pic in enumerate(pics):
            des.paste(pic, (0, i * h))
        return des


    @staticmethod
    def pic2b64(pic) -> str:
        buf = BytesIO()
        pic.save(buf, format='PNG')
        base64_str = str(base64.b64encode(buf.getvalue()), encoding='utf8')
        return f'base64://{base64_str}'
