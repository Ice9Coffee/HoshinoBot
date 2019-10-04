import random
from time import sleep

import nonebot
from nonebot import on_command, CommandSession, Message
from nonebot import on_natural_language, NLPSession, IntentCommand

from .kokkoro import gacha_10_aliases, gacha_1_aliases
from .util import silence

__private_hb_handler_cmd = '__hb_handler_' + hex(random.randint(0x1000000000000000, 0xffffffffffffffff))[2:]

ban_hb_title = []
ban_hb_title.extend(gacha_10_aliases)
ban_hb_title.extend(gacha_1_aliases)


bot = nonebot.get_bot()

@bot.on_message('group')
async def hb_handler(context):
    message = context['message']
    group_id = context['group_id']
    user_id = context['user_id']
    for m in message:
        if m['type'] == 'hb':
            try:
                title = m['data']['title']
                if title in ban_hb_title:
                    bot.set_group_ban(group_id=group_id, user_id=user_id, duration= 12*60*60)
                sleep(0.5 + 3 * random.random())
                await bot.send(context, title)
            except Exception as e:
                print(e)



'''
@on_command(__private_hb_handler_cmd)
async def hb_handler(session:CommandSession):
    pass


@on_natural_language(keywords={'[CQ:hb'}, only_to_me=False)
async def hb_listener(session:NLPSession):
    message = session.ctx['message']
    for m in message:
        if m['type'] == 'hb':
            try:
                title = m['data']['title']
                if title in ban_hb_title:
                    silence(session, 12*60*60, True)
                sleep(1 + 5 * random.random())
                session.send(title)
            except Exception as e:
                print(e)
'''