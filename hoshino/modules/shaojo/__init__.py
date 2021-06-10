import random
from hoshino import Service, util
from hoshino.typing import CQEvent
import time
from .choicer import Choicer

sv = Service('少女', enable_on_default=True, bundle='娱乐', help_='''今天也是少女!
[今天我是什么少女] 看看今天你是什么少女
[@xxx今天是什么少女] 看看xxx今天是什么少女''')

inst = Choicer(util.load_config(__file__))


@sv.on_fullmatch('今天我是什么少女')
async def my_shoujo(bot, ev: CQEvent):
    uid = ev.user_id
    name = ev.sender['card'] or ev.sender['nickname']
    msg = inst.format_msg(uid, name)
    await bot.send(ev, msg)


@sv.on_prefix('今天是什么少女')
@sv.on_suffix('今天是什么少女')
async def other_shoujo(bot, ev: CQEvent):
    arr = []
    for i in ev.message:
        if i['type'] == 'at' and i['data']['qq'] != 'all':
            arr.append(int(i['data']['qq']))
    gid = ev.group_id
    for uid in arr:
        info = await bot.get_group_member_info(
            group_id=gid,
            user_id=uid,
            no_cache=True
        )
        name = info['card'] or info['nickname']
        msg = inst.format_msg(uid, name)
        await bot.send(ev, msg)
