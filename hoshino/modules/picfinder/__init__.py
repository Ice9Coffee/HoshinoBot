import re
import asyncio
from asyncio import sleep
from datetime import datetime, timedelta

from nonebot import get_bot

import hoshino
from hoshino import Service, log, priv
from hoshino.typing import CQEvent
from hoshino.util import DailyNumberLimiter
from hoshino.config import NICKNAME
from aiocqhttp.exceptions import ActionFailed

from hoshino.config.picfinder import threshold, SAUCENAO_KEY, SEARCH_TIMEOUT, CHAIN_REPLY, DAILY_LIMIT, helptext, CHECK, enableguild, IGNORE_STAMP

if type(NICKNAME) == str:
    NICKNAME = [NICKNAME]

sv = Service('picfinder', help_=helptext)
from .image import get_image_data_sauce, get_image_data_ascii, check_screenshot

lmtd = DailyNumberLimiter(DAILY_LIMIT)
logger = sv.logger


class PicListener:
    def __init__(self):
        self.on = {}
        self.count = {}
        self.limit = {}
        self.timeout = {}

    def get_on_off_status(self, gid):
        return self.on[gid] if self.on.get(gid) is not None else False

    def turn_on(self, gid, uid):
        self.on[gid] = uid
        self.timeout[gid] = datetime.now()+timedelta(seconds=SEARCH_TIMEOUT)
        self.count[gid] = 0
        self.limit[gid] = DAILY_LIMIT-lmtd.get_num(uid)

    def turn_off(self, gid):
        self.on.pop(gid)
        self.count.pop(gid)
        self.timeout.pop(gid)
        self.limit.pop(gid)

    def count_plus(self, gid):
        self.count[gid] += 1


pls = PicListener()


@sv.on_prefix(('识图', '搜图', '查图', '找图'), only_to_me=True)
async def start_finder(bot, ev: CQEvent):
    uid = ev.user_id
    gid = ev.group_id
    mid = ev.message_id
    ret = None
    for m in ev.message:
        if m.type == 'image':
            file = m.data['file']
            url = m.data['url']
            if 'subType' in m.data:
                sbtype = m.data['subType']
            else:
                sbtype = None
            ret = 1
            break    
    if not ret:
        if pls.get_on_off_status(gid):
            if uid == pls.on[gid]:
                pls.timeout[gid] = datetime.now()+timedelta(seconds=30)
                await bot.finish(ev, f"您已经在搜图模式下啦！\n如想退出搜图模式请发送“谢谢星乃”~")
            else:
                await bot.finish(ev, f"本群[CQ:at,qq={pls.on[gid]}]正在搜图，请耐心等待~")
        pls.turn_on(gid, uid)
        await bot.send(ev, f"了解～请发送图片吧！支持批量噢！\n如想退出搜索模式请发送“谢谢{NICKNAME[0]}”")
        await sleep(30)
        ct = 0
        while pls.get_on_off_status(gid):
            if datetime.now() < pls.timeout[gid]:
                if ct != pls.count[gid]:
                    ct = pls.count[gid]
                    pls.timeout[gid] = datetime.now()+timedelta(seconds=60)
            else:
                temp = pls.on[gid]
                if not pls.count[gid]:
                    await bot.send(ev, f"[CQ:at,qq={temp}] 由于超时，已为您自动退出搜图模式~\n您本次搜索期间未发送任何图片，请检查是否被吞图~")
                else:
                    await bot.send(ev, f"[CQ:at,qq={temp}] 由于超时，已为您自动退出搜图模式，以后要记得说“谢谢{NICKNAME[0]}”来退出搜图模式噢~\n您本次搜索共搜索了{pls.count[gid]}张图片～")
                pls.turn_off(ev.group_id)
                break
            await sleep(30)
        return
    if not priv.check_priv(ev, priv.SUPERUSER):
        if not lmtd.check(uid):
            await bot.send(ev, f'您今天已经搜过{DAILY_LIMIT}次图了，休息一下明天再来吧~', at_sender=True)
            return

    if CHECK:
        result = await check_screenshot(bot, file, url)
        if result:
            if result == 1:
                await bot.send(ev, f'[CQ:reply,id={mid}]该图似乎是手机截屏，请进行适当裁剪后再尝试搜图~\n*请注意搜索漫画时务必截取一个完整单页进行搜图~')
            if result == 2:
                await bot.send(ev, f'[CQ:reply,id={mid}]该图似乎是长图拼接，请进行适当裁剪后再尝试搜图~\n*请注意搜索漫画时务必截取一个完整单页进行搜图~')
            return
    if 'c2cpicdw.qpic.cn/offpic_new/' in url:
        md5 = file[:-6].upper()
        url = f"http://gchat.qpic.cn/gchatpic_new/0/0-0-{md5}/0?term=2"
    await bot.send(ev, '正在搜索，请稍候～')
    await picfinder(bot, ev, url)


@sv.on_message('group')
async def picmessage(bot, ev: CQEvent):
    mid = ev.message_id
    atcheck = False
    batchcheck = False
    for m in ev.message:
        if m.type == 'at' and m.data['qq']==ev.self_id:
            atcheck = True
    if pls.get_on_off_status(ev.group_id):
        if int(pls.on[ev.group_id]) == int(ev.user_id):
            batchcheck = True
    if not(batchcheck or atcheck):
        return
    uid = ev.user_id
    ret = None
    for m in ev.message:
        if m.type == 'image':
            file = m.data['file']
            url = m.data['url']
            if 'subType' in m.data:
                sbtype=m.data['subType']
            else:
                sbtype=None
            ret=1
            break
    if not ret:
        return
    if not priv.check_priv(ev, priv.SUPERUSER):
        if not lmtd.check(uid):
            await bot.send(ev, f'您今天已经搜过{DAILY_LIMIT}次图了，休息一下明天再来吧～', at_sender=True)
            if pls.get_on_off_status(ev.group_id):
                pls.turn_off(ev.group_id)
                return
    if pls.get_on_off_status(ev.group_id):
        pls.count_plus(ev.group_id)
        if pls.count[ev.group_id] > pls.limit[ev.group_id]:
            await bot.send(ev, f'您今天已经搜过{DAILY_LIMIT}次图了，休息一下明天再来吧～', at_sender=True)
            pls.turn_off(ev.group_id)
            return
    if sbtype and IGNORE_STAMP:
        if sbtype!='0':
            await bot.send(ev, f'[CQ:reply,id={mid}]该图为表情，已忽略~如确需搜索请尝试单发搜索或回复搜索~')
            return

    if CHECK:
        result = await check_screenshot(bot, file, url)
        if result:
            if result == 1:
                await bot.send(ev, f'[CQ:reply,id={mid}]该图似乎是手机截屏，请手动进行适当裁剪后再尝试搜图~\n*请注意搜索漫画时务必截取一个完整单页进行搜图~')
            if result == 2:
                await bot.send(ev, f'[CQ:reply,id={mid}]该图似乎是长图拼接，请手动进行适当裁剪后再尝试搜图~\n*请注意搜索漫画时务必截取一个完整单页进行搜图~')
            return
    if 'c2cpicdw.qpic.cn/offpic_new/' in url:
        md5 = file[:-6].upper()
        url = f"http://gchat.qpic.cn/gchatpic_new/0/0-0-{md5}/0?term=2"
    await bot.send(ev, '正在搜索，请稍候～')
    await picfinder(bot, ev, url)


@sv.on_message('group')
async def replymessage(bot, ev: CQEvent):
    mid = ev.message_id
    uid = ev.user_id
    if not ev.message:
        sv.logger.error(f"message is empty: {ev.raw_message}")
        return
    seg = ev.message[0]
    if seg.type != 'reply':
        return
    tmid = seg.data['id']
    cmd = ev.message.extract_plain_text()
    is_at_me = 0
    flag2 = 0
    for m in ev.message[2:]:
        if m.type == 'at' and m.data['qq'] == ev.self_id:
            is_at_me = 1
    for name in NICKNAME:
        if name in cmd:
            is_at_me = 1
            break
    for pfcmd in ['识图', '搜图', '查图', '找图']:
        if pfcmd in cmd:
            flag2 = 1
    if not (is_at_me and flag2):
        return
    if not priv.check_priv(ev, priv.SUPERUSER):
        if not lmtd.check(uid):
            await bot.send(ev, f'您今天已经搜过{DAILY_LIMIT}次图了，休息一下明天再来吧～', at_sender=True)
    try:
        tmsg = await bot.get_msg(self_id=ev.self_id, message_id=int(tmid))
    except ActionFailed:
        await bot.finish(ev, '该消息已过期，请重新转发~')
    file = ''
    print(tmsg)
    for m in tmsg["message"]:
        if m["type"] == 'image':
            file=m['file']
            url=m['url']
            subType=m['subType']
            break
    if not file:
        await bot.send(ev, '未找到图片~')
        return
        
    if CHECK:
        result = await check_screenshot(bot, file, url)
        if result:
            if result == 1:
                await bot.send(ev, f'[CQ:reply,id={mid}]该图似乎是手机截屏，请手动进行适当裁剪后再尝试搜图~\n*请注意搜索漫画时务必截取一个完整单页进行搜图~')
            if result == 2:
                await bot.send(ev, f'[CQ:reply,id={mid}]该图似乎是长图拼接，请手动进行适当裁剪后再尝试搜图~\n*请注意搜索漫画时务必截取一个完整单页进行搜图~')
            return
    if 'c2cpicdw.qpic.cn/offpic_new/' in url:
        md5 = file[:-6].upper()
        url = f"http://gchat.qpic.cn/gchatpic_new/0/0-0-{md5}/0?term=2"
    await bot.send(ev, '正在搜索，请稍候～')
    await picfinder(bot, ev, url)


@sv.on_prefix('谢谢')
async def thanks(bot, ev: CQEvent):
    gid = ev.group_id
    name = ev.message.extract_plain_text().strip()
    if name not in NICKNAME:
        return
    if pls.get_on_off_status(gid):
        if pls.on[gid] != ev.user_id:
            await bot.send(ev, '不能替别人结束搜图哦～')
            return
        if not pls.count[gid]:
            await bot.send(ev, f"不用谢～\n您本次搜索期间未发送任何图片，请检查是否被吞图～")
        else:
            await bot.send(ev, f'不用谢～\n您本次搜索共搜索了{pls.count[gid]}张图片～')
        pls.turn_off(gid)
        print('turned off')
        return
    await bot.send(ev, 'にゃ～')

async def gsend(ev: CQEvent, msg):
    hbot = hoshino.get_bot()
    return await hbot.send_guild_channel_msg(
                        guild_id=ev.guild_id,
                        channel_id=ev.channel_id,
                        message=msg,
                        self_id=ev.self_id
                    )

async def chain_reply(bot, ev, chain, msg):
    if ev.detail_type == 'guild':
        await gsend(ev, msg)
        return chain
    if not CHAIN_REPLY:
        await bot.send(ev, msg)
        return chain
    else:
        data = {
            "type": "node",
            "data": {
                    "name": str(NICKNAME[0]),
                    "user_id": str(ev.self_id),
                    "content": str(msg)
            }
        }
        chain.append(data)
        return chain


async def picfinder(bot, ev, image_data):
    uid = ev.user_id
    chain = []
    result = await get_image_data_sauce(image_data, SAUCENAO_KEY)
    image_data_report = result[0]
    simimax = result[1]
    if 'Index #' in image_data_report:
        await bot.send_private_msg(self_id=ev.self_id, user_id=bot.config.SUPERUSERS[0], message='发生index解析错误')
        await bot.send_private_msg(self_id=ev.self_id, user_id=bot.config.SUPERUSERS[0], message=image_data)
        await bot.send_private_msg(self_id=ev.self_id, user_id=bot.config.SUPERUSERS[0], message=image_data_report)
    chain = await chain_reply(bot, ev, chain, image_data_report)

    if float(simimax) > float(threshold):
        lmtd.increase(uid)
    else:
        if simimax != 0:
            chain = await chain_reply(bot, ev, chain, "相似度过低，换用ascii2d检索中…")
        else:
            logger.error("SauceNao not found imageInfo")
            chain = await chain_reply(bot, ev, chain, 'SauceNao检索失败,换用ascii2d检索中…')

        image_data_report = await get_image_data_ascii(image_data)
        if image_data_report[0]:
            chain = await chain_reply(bot, ev, chain, image_data_report[0])
            lmtd.increase(uid)
        if image_data_report[1]:
            chain = await chain_reply(bot, ev, chain, image_data_report[1])
        if not (image_data_report[0] or image_data_report[1]):
            logger.error("ascii2d not found imageInfo")
            chain = await chain_reply(bot, ev, chain, 'ascii2d检索失败…')

    if CHAIN_REPLY and (ev.detail_type != 'guild'):
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=chain)


'''
bot = get_bot()


@bot.on_message('private')
async def picprivite(ctx: CQEvent):
    type = ctx["sub_type"]
    sid = int(ctx["self_id"])
    uid = int(ctx["sender"]["user_id"])
    gid = 0
    if priv.check_block_user(uid):
        return
    ret = None
    for m in ctx.message:
        if m.type == 'image':
            file = m.data['file']
            url = m.data['url']
            if 'subType' in m.data:
                sbtype=m.data['subType']
            else:
                sbtype=None
            ret=1
            break
    if not ret:
        flag1 = flag2 = 0
        for name in NICKNAME:
            if name in str(ctx['message']):
                flag1 = 1
                break
        for pfcmd in ['识图', '搜图', '查图', '找图']:
            if pfcmd in str(ctx['message']):
                flag2 = 1
        if flag1 and flag2:
            await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message=f'私聊搜图请直接发送图片~')
        return
    if not lmtd.check(uid):
        await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message=f'您今天已经搜过{DAILY_LIMIT}次图了，休息一下明天再来吧~')
        return
    if 'c2cpicdw.qpic.cn/offpic_new/' in url:
        md5 = file[:-6].upper()
        url = f"http://gchat.qpic.cn/gchatpic_new/0/0-0-{md5}/0?term=2"
    if type == "group":
        gid = int(ctx["sender"]["group_id"])
        await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message='临时会话含图片与网址消息极大概率被吞，如搜图结果无法显示请换用群聊搜索或添加bot好友~')
    await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message='正在搜索，请稍候～')
    result = await get_image_data_sauce(url, SAUCENAO_KEY)
    image_data_report = result[0]
    simimax = result[1]
    if 'Index #' in image_data_report:
        await bot.send_private_msg(self_id=sid, user_id=bot.config.SUPERUSERS[0], message='发生index解析错误')
        await bot.send_private_msg(self_id=sid, user_id=bot.config.SUPERUSERS[0], message=url)
        await bot.send_private_msg(self_id=sid, user_id=bot.config.SUPERUSERS[0], message=image_data_report)
    await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message=image_data_report)

    if float(simimax) > float(threshold):
        lmtd.increase(uid)
    else:
        if simimax != 0:
            await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message="相似度过低，换用ascii2d检索中…")
        else:
            logger.error("SauceNao not found imageInfo")
            await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message='SauceNao检索失败,换用ascii2d检索中…')

        image_data_report = await get_image_data_ascii(url)
        if image_data_report[0]:
            await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message=image_data_report[0])
            lmtd.increase(uid)
        if image_data_report[1]:
            await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message=image_data_report[1])
        if not (image_data_report[0] or image_data_report[1]):
            logger.error("ascii2d not found imageInfo")
            await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message='ascii2d检索失败…')


@bot.on_message('guild')
async def gpicfinder(ev: CQEvent):
    if (tid := ev.user_id) == ev.self_tiny_id:
        return
    if int(ev.channel_id) not in enableguild.get(int(ev.guild_id), []):
        return
    ret = []
    for i in ev.message:
        if i['type'] == 'image':
            ret.append(i['data']['url'])
    if not ret:
        return
    if not lmtd.check(tid):
        await gsend(ev, f'您今天已经搜过{DAILY_LIMIT}次图了，休息一下明天再来吧～')
        return
    await gsend(ev, '正在搜索，请稍候～')
    bot = hoshino.get_bot()
    for url in ret:
        asyncio.get_event_loop().create_task(picfinder(bot, ev, url))

'''