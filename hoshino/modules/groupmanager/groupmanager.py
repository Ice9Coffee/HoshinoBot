from hoshino import Service, priv, R
from hoshino.util import DailyNumberLimiter

import random

from . import util

sv_help = '''
- [申请头衔XX] XX为头衔名
- [删除头衔] 删除自己获得的头衔,可以@其他人
- [禁言@sb XX] sb就是sb , xx为秒数
- [解除禁言@sb] 字面意思
- [全员禁言] 开启全员禁言
- [飞机票@sb] 把sb请出本群
- [设置管理员 @sb] 
- [取消管理员 @sb] 
- [修改名片@sb xxx] 吧sb的群名片设置为xxx
- [发送群公告 XXX]
'''.strip()

sv = Service(
    name='群管',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # False隐藏
    enable_on_default=True,  # 是否默认启用
    bundle='通用',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助-群管"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


@sv.on_prefix('申请头衔')
async def special_title(bot, ev):
    uid = ev.user_id
    sid = None
    gid = ev.group_id
    title = ev.message.extract_plain_text()
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
    if sid is None:
        sid = uid
    await util.title_get(bot, ev, uid, sid, gid, title)


@sv.on_fullmatch(('删除头衔', '清除头衔', '收回头衔', '回收头衔', '取消头衔'))
async def del_special_title(bot, ev):
    uid = ev.user_id
    sid = None
    gid = ev.group_id
    title = None
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
    if sid is None:
        sid = uid
    await util.title_get(bot, ev, uid, sid, gid, title)


#####

@sv.on_prefix(('来发口球', '塞口球', '禁言一下', '禁言', '口球', '黑屋'))
async def umm_ahh(bot, ev):
    uid = ev.user_id
    sid = None
    gid = ev.group_id
    time = ev.message.extract_plain_text().strip()
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
        elif m.type == 'at' and m.data['qq'] == 'all':
            await util.gruop_silence(bot, ev, gid, True)
            return
    if sid is None:
        sid = uid
    await util.member_silence(bot, ev, uid, sid, gid, time)


@sv.on_prefix(('解除口球', '取消口球', '摘口球', '脱口球', '取消禁言', '解除禁言', '摘下口球', '解禁'))
async def cancel_ban_member(bot, ev):
    uid = ev.user_id
    gid = ev.group_id
    sid = None
    time = '0'
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
        elif m.type == 'at' and m.data['qq'] == 'all':
            await util.gruop_silence(bot, ev, gid, False)
            return
    if sid is None:
        await bot.send(ev, '请@需要摘口球的群员哦w')
        return
    await util.member_silence(bot, ev, uid, sid, gid, time)


####  
@sv.on_prefix(('设置管理员', '设置管理', '右迁', '升职'))
async def set_admin(bot, ev):
    uid = ev.user_id
    sid = None
    gid = ev.group_id
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
        elif m.type == 'at' and m.data['qq'] == 'all':
            await bot.send(ev, '你一定是喝醉了~', at_sender=True)
            return
    if sid is None:
        await bot.send(ev, '请@需要成为管理的成员哦')
        return
    await util.admin_set(bot, ev, sid, gid, True)


@sv.on_prefix(('取消管理员', '取消管理', '左迁', '降职'))
async def unset_admin(bot, ev):
    uid = ev.user_id
    sid = None
    gid = ev.group_id
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
        elif m.type == 'at' and m.data['qq'] == 'all':
            await bot.send(ev, '你清醒点!!!', at_sender=True)
            return
    if sid is None:
        await bot.send(ev, '请@需要取消管理的成员哦')
        return
    await util.admin_set(bot, ev, sid, gid, False)


@sv.on_fullmatch(('全员口球', '全员禁言'))
async def ban_all(bot, ev):
    gid = ev.group_id
    status = True
    await util.gruop_silence(bot, ev, gid, status)


@sv.on_fullmatch(('取消全员口球', '取消全员禁言', '解除全员口球', '解除全员禁言'))
async def cancel_ban_all(bot, ev):
    gid = ev.group_id
    status = False
    await util.gruop_silence(bot, ev, gid, status)


@sv.on_prefix(('来张飞机票', '踢出本群', '移出本群', '踢出此群', '移出群聊', '飞机票', '飞机', '滚'))
async def guoup_kick(bot, ev):
    uid = ev.user_id
    gid = ev.group_id
    sid = None
    is_reject = False
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
        elif m.type == 'at' and m.data['qq'] == 'all':
            await bot.send(ev, '人干事？', at_sender=True)
            return
    if sid is None:
        sid = uid
        await bot.send(ev, '后面@需要踢走的人', at_sender=True)
        return
    await util.member_kick(bot, ev, uid, sid, gid, is_reject)


@sv.on_prefix(('修改名片', '修改群名片', '设置名片', '设置群名片'))
async def card_set(bot, ev):
    uid = ev.user_id
    sid = None
    gid = ev.group_id
    card_text = ev.message.extract_plain_text()
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
    if sid is None:
        sid = uid
    await util.card_edit(bot, ev, uid, sid, gid, card_text)


@sv.on_prefix(('修改群名', '设置群名'))
async def set_group_name(bot, ev):
    gid = ev.group_id
    uid = ev.user_id
    name = ev.message.extract_plain_text()
    await util.group_name(bot, ev, gid, name)


@sv.on_prefix(('发送公告', '设置公告'))
async def send_group_notice(bot, ev):
    gid = ev.group_id
    uid = ev.user_id
    text = ev.message.extract_plain_text()
    await util.group_notice(bot, ev, gid, text)
