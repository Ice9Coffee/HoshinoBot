import os
import base64
import ujson as json

from io import BytesIO
from PIL import Image

import zhconv

from .priconne_data import _PriconneData
from hoshino.log import logger
from hoshino.res import R, ResImg


gadget_equip = R.img('priconne/gadget/equip.png').toPILImage()
gadget_star = R.img('priconne/gadget/star.png').toPILImage()
gadget_star_dis = R.img('priconne/gadget/star_disabled.png').toPILImage()
gadget_star_pink = R.img('priconne/gadget/star_pink.png').toPILImage()
unknown_chara_icon = R.img('priconne/unit/icon_unit_100031.png').toPILImage()

NAME2ID = {}

def gen_name2id():
    NAME2ID.clear()
    for k, v in _PriconneData.CHARA.items():
        for s in v:
            if s not in NAME2ID:
                NAME2ID[normname(s)] = k
            else:
                logger.warning(f'Chara.__gen_name2id: 出现重名{s}于id{k}与id{NAME2ID[s]}')


def normname(name:str) -> str:
    name = name.lower().replace('（', '(').replace('）', ')')
    name = zhconv.convert(name, 'zh-hans')
    return name

class Chara:
    
    UNKNOWN = 1000
    
    def __init__(self, id_, star=3, equip=0):
        self.id = id_
        self.star = star
        self.equip = equip


    @staticmethod
    def fromid(id_, star=3, equip=0):
        '''Create Chara from her id. The same as Chara()'''
        return Chara(id_, star, equip)


    @staticmethod
    def fromname(name, star=3, equip=0):
        '''Create Chara from her name.'''
        id_ = Chara.name2id(name)
        return Chara(id_, star, equip)


    @property
    def name(self):
        return _PriconneData.CHARA[self.id][0] if self.id in _PriconneData.CHARA else _PriconneData.CHARA[Chara.UNKNOWN][0]


    @property
    def icon(self) -> ResImg:
        star = '6' if 6 <= self.star else '3' # if 3 <= self.star else '1' if 1 <= self.star else '3'
        id_ = self.id
        if not 1000 < id_ < 2000:
            id_ = Chara.UNKNOWN
        return R.img(f'priconne/unit/icon_unit_{id_}{star}1.png')


    def gen_icon_img(self, size, star_slot_verbose=True) -> Image:
        try:
            pic = self.icon.toPILImage().convert('RGBA').resize((size, size), Image.LANCZOS)
        except FileNotFoundError:
            logger.error(f'File not found: {self.icon.path}')
            pic = unknown_chara_icon.convert('RGBA').resize((size, size), Image.LANCZOS)

        l = size // 6
        star_lap = round(l * 0.15)
        margin_x = ( size - 6*l ) // 2
        margin_y = round(size * 0.05)
        if self.star:
            for i in range(5 if star_slot_verbose else min(self.star, 5)):
                a = i*(l-star_lap) + margin_x
                b = size - l - margin_y
                s = gadget_star if self.star > i else gadget_star_dis
                s = s.resize((l, l), Image.LANCZOS)
                pic.paste(s, (a, b, a+l, b+l), s)
            if 6 == self.star:
                a = 5*(l-star_lap) + margin_x
                b = size - l - margin_y
                s = gadget_star_pink
                s = s.resize((l, l), Image.LANCZOS)
                pic.paste(s, (a, b, a+l, b+l), s)
        l = round(l * 1.5)
        if self.equip:
            a = margin_x
            b = margin_x
            s = gadget_equip.resize((l, l), Image.LANCZOS)
            pic.paste(s, (a, b, a+l, b+l), s)
        return pic


    @staticmethod
    def gen_team_pic(team, size=128, star_slot_verbose=True):
        num = len(team)
        des = Image.new('RGBA', (num*size, size), (255, 255, 255, 255))
        for i, chara in enumerate(team):
            src = chara.gen_icon_img(size, star_slot_verbose)
            des.paste(src, (i * size, 0), src)
        return des


    @staticmethod
    def name2id(name):
        name = normname(name)
        if not NAME2ID:
            gen_name2id()
        return NAME2ID[name] if name in NAME2ID else Chara.UNKNOWN
