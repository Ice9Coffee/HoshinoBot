import importlib
from io import BytesIO

import pygtrie
import requests
from fuzzywuzzy import fuzz, process
from PIL import Image

import hoshino
from hoshino import R, log, sucmd, util
from hoshino.typing import CommandSession

from . import _pcr_data

logger = log.new_logger('chara', hoshino.config.DEBUG)
UNKNOWN = 1000
UnavailableChara = {
    1069,   # 霸瞳
    1072,   # 可萝爹
    1073,   # 拉基拉基
    1102,   # 泳装大眼
    1183,   # 星弓星
    1184,   # 星弓栞
    1204,   # 小小甜心美美
    1205,   # 小小甜心禊
    1206,   # 小小甜心镜华
}

try:
    gadget_equip = R.img('priconne/gadget/equip.png').open()
    gadget_star = R.img('priconne/gadget/star.png').open()
    gadget_star_dis = R.img('priconne/gadget/star_disabled.png').open()
    gadget_star_pink = R.img('priconne/gadget/star_pink.png').open()
    unknown_chara_icon = R.img(f'priconne/unit/icon_unit_{UNKNOWN}31.png').open()
except Exception as e:
    logger.exception(e)


class Roster:

    def __init__(self):
        self._roster = pygtrie.CharTrie()
        self.update()
    
    def update(self):
        importlib.reload(_pcr_data)
        self._roster.clear()
        for idx, names in _pcr_data.CHARA_NAME.items():
            for n in names:
                n = util.normalize_str(n)
                if n not in self._roster:
                    self._roster[n] = idx
                else:
                    logger.warning(f'priconne.chara.Roster: 出现重名{n}于id{idx}与id{self._roster[n]}')
        self._all_name_list = self._roster.keys()


    def get_id(self, name):
        name = util.normalize_str(name)
        return self._roster[name] if name in self._roster else UNKNOWN


    def guess_id(self, name):
        """@return: id, name, score"""
        name, score = process.extractOne(name, self._all_name_list, processor=util.normalize_str)
        return self._roster[name], name, score


    def parse_team(self, namestr):
        """@return: List[ids], unknown_namestr"""
        namestr = util.normalize_str(namestr.strip())
        team = []
        unknown = []
        while namestr:
            item = self._roster.longest_prefix(namestr)
            if not item:
                unknown.append(namestr[0])
                namestr = namestr[1:].lstrip()
            else:
                team.append(item.value)
                namestr = namestr[len(item.key):].lstrip()
        return team, ''.join(unknown)


roster = Roster()

def name2id(name):
    return roster.get_id(name)

def fromid(id_, star=0, equip=0):
    return Chara(id_, star, equip)

def fromname(name, star=0, equip=0):
    id_ = name2id(name)
    return Chara(id_, star, equip)

def guess_id(name):
    """@return: id, name, score"""
    return roster.guess_id(name)

def is_npc(id_):
    if id_ in UnavailableChara:
        return True
    else:
        return not ((1000 < id_ < 1300) or (1700 < id_ < 1900))

def gen_team_pic(team, size=64, star_slot_verbose=True):
    num = len(team)
    des = Image.new('RGBA', (num*size, size), (255, 255, 255, 255))
    for i, chara in enumerate(team):
        src = chara.render_icon(size, star_slot_verbose)
        des.paste(src, (i * size, 0), src)
    return des


def download_chara_icon(id_, star):
    url = f'https://redive.estertion.win/icon/unit/{id_}{star}1.webp'
    save_path = R.img(f'priconne/unit/icon_unit_{id_}{star}1.png').path
    logger.info(f'Downloading chara icon from {url}')
    try:
        rsp = requests.get(url, stream=True, timeout=5)
    except Exception as e:
        logger.error(f'Failed to download {url}. {type(e)}')
        logger.exception(e)
    if 200 == rsp.status_code:
        img = Image.open(BytesIO(rsp.content))
        img.save(save_path)
        logger.info(f'Saved to {save_path}')
    else:
        logger.error(f'Failed to download {url}. HTTP {rsp.status_code}')


class Chara:

    def __init__(self, id_, star=0, equip=0):
        self.id = id_
        self.star = star
        self.equip = equip

    @property
    def name(self):
        return _pcr_data.CHARA_NAME[self.id][0] if self.id in _pcr_data.CHARA_NAME else _pcr_data.CHARA_NAME[UNKNOWN][0]

    @property
    def is_npc(self) -> bool:
        return is_npc(self.id)

    @property
    def icon(self):
        star = '3' if 1 <= self.star <= 5 else '6'
        res = R.img(f'priconne/unit/icon_unit_{self.id}{star}1.png')
        if not res.exist:
            res = R.img(f'priconne/unit/icon_unit_{self.id}31.png')
        if not res.exist:
            res = R.img(f'priconne/unit/icon_unit_{self.id}11.png')
        if not res.exist:   # FIXME: 不方便改成异步请求
            download_chara_icon(self.id, 6)
            download_chara_icon(self.id, 3)
            download_chara_icon(self.id, 1)
            res = R.img(f'priconne/unit/icon_unit_{self.id}{star}1.png')
        if not res.exist:
            res = R.img(f'priconne/unit/icon_unit_{self.id}31.png')
        if not res.exist:
            res = R.img(f'priconne/unit/icon_unit_{self.id}11.png')
        if not res.exist:
            res = R.img(f'priconne/unit/icon_unit_{UNKNOWN}31.png')
        return res


    def render_icon(self, size, star_slot_verbose=True) -> Image:
        try:
            pic = self.icon.open().convert('RGBA').resize((size, size), Image.LANCZOS)
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
        if self.equip:
            l = round(l * 1.5)
            a = margin_x
            b = margin_x
            s = gadget_equip.resize((l, l), Image.LANCZOS)
            pic.paste(s, (a, b, a+l, b+l), s)
        return pic



@sucmd('reload-pcr-chara', force_private=False, aliases=('重载花名册', ))
async def reload_pcr_chara(session: CommandSession):
    try:
        roster.update()
        await session.send('ok')
    except Exception as e:
        logger.exception(e)
        await session.send(f'Error: {type(e)}')


@sucmd('download-pcr-chara-icon', force_private=False, aliases=('下载角色头像'))
async def download_pcr_chara_icon(session: CommandSession):
    try:
        id_ = roster.get_id(session.current_arg_text.strip())
        assert id_ != UNKNOWN, '未知角色名'
        download_chara_icon(id_, 6)
        download_chara_icon(id_, 3)
        download_chara_icon(id_, 1)
        await session.send('ok')
    except Exception as e:
        logger.exception(e)
        await session.send(f'Error: {type(e)}')
