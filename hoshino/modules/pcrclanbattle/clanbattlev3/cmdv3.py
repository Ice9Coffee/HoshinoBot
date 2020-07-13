from hoshino import Service, priv
from hoshino.typing import *

from .battlemaster import BattleMaster as Master
from .const import *

sv = Service('clanbattlev3', bundle='pcr会战', help_='Hoshino会战管理v3（建设中）')

ERROR_CLAN_NOTFOUND = f'公会未初始化：请群管理发送"建会日/台/B服"'
ERROR_ZERO_MEMBER = f'公会内无成员：请使用"入会"或"批量入会"以添加'
ERROR_MEMBER_NOTFOUND = f'未找到成员：请使用"入会"以添加'
ERROR_PERMISSION_DENIED = '权限不足：需*群管理*以上权限'

# =============== helper functions ================= #

async def _check_clan(bot, ev, bm: Master):
    clan = bm.get_clan()
    if not clan:
        await bot.finish(ev, ERROR_CLAN_NOTFOUND)
    return clan

async def _check_member(bot, ev, bm: Master, uid:int, alt:int, tip=None):
    mem = bm.get_member(uid, alt) or bm.get_member(uid, 0) # 兼容cmdv1
    if not mem:
        await bot.finish(ev, tip or ERROR_MEMBER_NOTFOUND)
    return mem

async def _check_admin(bot, ev, tip:str=''):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, ERROR_PERMISSION_DENIED + tip)

# ================================================== #

async def add_clan(bot, ev, server):
    await _check_admin(bot, ev, '才能建会')
    

@sv.on_prefix('建会日服')
async def _(bot, ev):
    await add_clan(bot, ev, SERVER.JP)

@sv.on_prefix('建会台服')
async def _(bot, ev):
    await add_clan(bot, ev, SERVER.JP)

@sv.on_prefix(('建会B服', '建会陆服'))
async def _(bot, ev):
    await add_clan(bot, ev, SERVER.JP)
