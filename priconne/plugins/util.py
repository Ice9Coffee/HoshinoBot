import os
import logging
import base64
import json

from io import BytesIO
from PIL import Image
from urllib.parse import urljoin, quote

from typing import List

from nonebot import on_command, CommandSession, MessageSegment
from nonebot.permission import check_permission, SUPERUSER
from aiocqhttp.exceptions import ActionFailed
from ._priconne_data import _PriconneData

USE_PRO_VERSION = True      # 是否使用酷Q PRO版功能，如撤回、发图等


def get_config():
    config_file = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_file) as f:
        config = json.load(f)
        return config

def get_img_bed():
    return get_config()["IMG_BED"]

def get_local_unit_img(filename):
    return os.path.join(get_config()["LOCAL_IMG_DIR"], './unit/', filename)

def get_local_gadget_img(filename):
    return os.path.join(get_config()["LOCAL_IMG_DIR"], './gadget/', filename)


async def delete_msg(session:CommandSession):
    try:
        if USE_PRO_VERSION:
            msg_id = session.ctx['message_id']
            await session.bot.delete_msg(message_id=msg_id)
    except ActionFailed as e:
        print('retcode=', e.retcode, ' 撤回消息需要酷Q Pro版以及管理员权限')


async def silence(session:CommandSession, ban_time, ignore_super_user=False):
    group_id = session.ctx['group_id']
    user_id = session.ctx['user_id']
    if ignore_super_user or not await check_permission(session.bot, session.ctx, SUPERUSER):
        await session.bot.set_group_ban(group_id=group_id, user_id=user_id, duration=ban_time)


def get_cqimg(filename, path='', img_bed=None):
    if not img_bed:
        img_bed = get_img_bed()
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
    gadget_equip = Image.open(get_local_gadget_img('equip.png'))
    gadget_star = Image.open(get_local_gadget_img('star.png'))
    gadget_star_dis = Image.open(get_local_gadget_img('star_disabled.png'))
    gadget_star_pink = Image.open(get_local_gadget_img('star_pink.png'))


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
    def get_picname(id_, star=3, file_type='png') -> str:
        pic_pre = 'icon_unit_'
        pic_end = f'{star}1.{file_type}'
        if not 1000 < id_ < 2000:
            id_ = CharaHelper.UNKNOWN_CHARA      # unknown character
        return f'{pic_pre}{id_:0>4d}{pic_end}'


    @staticmethod
    def name2picname(name:str) -> str:
        id_ = CharaHelper.get_id(name)
        if not 1000 < id_ < 2000:
            id_ = CharaHelper.UNKNOWN_CHARA      # unknown character
        return CharaHelper.get_picname(id_)


    # 已废弃
    # @staticmethod
    # def gen_pic_base64(ids, size=128):
    #     pic = CharaHelper.gen_team_pic(ids, size)
    #     return CharaHelper.pic2b64(pic)


    @staticmethod
    def gen_chara_pic(id_, size, star=0, equip=0, star_slot_verbose=True):
        path = get_local_unit_img(CharaHelper.get_picname(id_, 6 if star == 6 else 3))
        pic = Image.open(path).convert('RGBA').resize((size, size), Image.LANCZOS)

        l = size // 6
        star_lap = round(l * 0.15)
        margin_x = ( size - 6*l ) // 2
        margin_y = margin_x + 5
        if star:
            for i in range(5 if star_slot_verbose else min(star, 5)):
                a = i*(l-star_lap) + margin_x
                b = size - l - margin_y
                s = CharaHelper.gadget_star if star > i else CharaHelper.gadget_star_dis
                s = s.resize((l, l), Image.LANCZOS)
                # print('paste', s, 'to', pic)
                pic.paste(s, (a, b, a+l, b+l), s)
            if 6 == star:
                a = 5*(l-star_lap) + margin_x
                b = size - l - margin_y
                s = CharaHelper.gadget_star_pink
                s = s.resize((l, l), Image.LANCZOS)
                pic.paste(s, (a, b, a+l, b+l), s)
        l = round(l * 1.5)
        if equip:
            a = margin_x
            b = margin_x
            s = CharaHelper.gadget_equip.resize((l, l), Image.LANCZOS)
            # print('paste', s, 'to', pic)
            pic.paste(s, (a, b, a+l, b+l), s)
        return pic


    @staticmethod
    def gen_team_pic(team, size=128, star_slot_verbose=True):
        '''
        team = List[(id_, star, equip)]
        '''
        num = len(team)
        des = Image.new('RGBA', (num*size, size), (255, 255, 255, 255))
        for i, chara in enumerate(team):
            if not isinstance(chara, (tuple, list)):
                if isinstance(chara, int):
                    chara = (chara, 0, 0)
                else:
                    raise ValueError('items in team must be an int or a tuple of (id_, star, equip)')
            src = CharaHelper.gen_chara_pic(chara[0], size, chara[1], chara[2], star_slot_verbose)
            des.paste(src, (i * size, 0), src)
        return des


    @staticmethod
    def concat_team_pic(pics, border=5):
        num = len(pics)
        w, h = pics[0].size
        des = Image.new('RGBA', (w, num * h + (num-1) * border), (255, 255, 255, 255))
        for i, pic in enumerate(pics):
            des.paste(pic, (0, i * (h + border)), pic)
        return des


    @staticmethod
    def pic2b64(pic) -> str:
        buf = BytesIO()
        pic.save(buf, format='PNG')
        base64_str = str(base64.b64encode(buf.getvalue()), encoding='utf8')
        return f'base64://{base64_str}'
