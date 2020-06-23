import importlib
from PIL import Image
from hoshino import R, log, sucmd, util
from hoshino.typing import CommandSession
from . import _data

UNKNOWN = 1000
logger = log.new_logger('chara')

class Roster:

    def __init__(self):
        self._roster = {}
        self.update()
    
    def update(self):
        importlib.reload(_data)
        self._roster.clear()
        for idx, names in _data.CHARA_NAME.items():
            for n in names:
                n = util.normalize_str(n)
                if n not in self._roster:
                    self._roster[n] = idx
                else:
                    logger.warning(f'priconne.chara.Roster: 出现重名{n}于id{idx}与id{self._roster[n]}')

    def get_id(self, name):
        name = util.normalize_str(name)
        return self._roster[name] if name in self._roster else UNKNOWN



roster = Roster()

def name2id(name):
    return roster.get_id(name)

def fromid(id_, star=3, equip=0):
    return Chara(id_, star, equip)

def fromname(name, star=3, equip=0):
    id_ = name2id(name)
    return Chara(id_, star, equip)

def gen_team_pic(team, size=64, star_slot_verbose=True):
    num = len(team)
    des = Image.new('RGBA', (num*size, size), (255, 255, 255, 255))
    for i, chara in enumerate(team):
        src = chara.render_icon(size, star_slot_verbose)
        des.paste(src, (i * size, 0), src)
    return des


try:
    gadget_equip = R.img('priconne/gadget/equip.png').open()
    gadget_star = R.img('priconne/gadget/star.png').open()
    gadget_star_dis = R.img('priconne/gadget/star_disabled.png').open()
    gadget_star_pink = R.img('priconne/gadget/star_pink.png').open()
    unknown_chara_icon = R.img('priconne/unit/icon_unit_100031.png').open()
except Exception as e:
    logger.exception(e)



UnavailableChara = (
    1067,   # 穗希
    1068,   # 晶
    1069,   # 霸瞳
    1072,   # 可萝爹
    1073,   # 拉基拉基
    1102,   # 泳装大眼
)

class Chara:

    def __init__(self, id_, star=3, equip=0):
        self.id = id_
        self.star = star
        self.equip = equip

    @property
    def name(self):
        return _data.CHARA_NAME[self.id][0] if self.id in _data.CHARA_NAME else _data.CHARA_NAME[UNKNOWN][0]

    @property
    def is_npc(self) -> bool:
        if self.id in UnavailableChara:
            return True
        else:
            return ~(1000 < self.id < 1200 or 1800 < self.id < 1900)


    @property
    def icon(self):
        star = '3' if 1 <= self.star <= 5 else '6'
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



@sucmd('reload-pcr-chara', aliases=('重载角色花名册'))
async def reload_pcr_chara(session: CommandSession):
    try:
        roster.update()
        await session.send('ok')
    except Exception as e:
        logger.exception(e)
        await session.send(f'Error: {type(e)}')
