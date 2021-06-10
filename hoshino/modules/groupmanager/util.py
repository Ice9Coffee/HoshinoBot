import hoshino
from hoshino import priv

from . import *

#获取指定群成员信息
async def group_member_info(bot, ev, gid, uid):
    try:
        gm_info = await bot.get_group_member_info(
            group_id = gid,
            user_id = uid,
            no_cache = True
        )
        return gm_info
    except Exception as e:
        hoshino.logger.exception(e)

#获取Bot的群信息
async def self_member_info(bot, ev, gid):
    info = await bot.get_login_info()
    self_id = info["user_id"]
    try:
        gm_info = await bot.get_group_member_info(
            group_id = gid,
            user_id = self_id,
            no_cache = True
        )
        return gm_info
    except Exception as e:
        hoshino.logger.exception(e)

#群荣誉信息
async def honor_info(bot, ev, gid, honor_type):
    try:
        gh_info = await bot.get_group_honor_info(
            group_id = gid,
            type = honor_type
        )
        return gh_info
    except Exception as e:
        hoshino.logger.exception(e)

#全员禁言
async def gruop_silence(bot, ev, gid, status):
    self_info = await self_member_info(bot, ev, gid)
    if self_info['role'] != 'owner' and self_info['role'] != 'admin':
        await bot.send(ev, '\n不给我管理员？', at_sender=True)
        return    
    if not priv.check_priv(ev,priv.ADMIN):
        await bot.send(ev, '只有管理才能给大家塞口球哦w', at_sender=True) 
    else:   
        try:
            await bot.set_group_whole_ban(
                    group_id = gid,
                    enable = status
                )
            if not status:
                await bot.send(ev, '全员禁言取消啦w')
            else:
                await bot.send(ev, '嘻嘻大家都被塞口球啦~')
        except Exception as e:
            await bot.send(ev, f'操作失败惹...\n错误代码：{e}', at_sender=True)

#单人禁言
async def member_silence(bot, ev, uid, sid, gid, time):
    self_info = await self_member_info(bot, ev, gid)
    if self_info['role'] != 'owner' and self_info['role'] != 'admin':
        await bot.send(ev, '\n不给我管理员？', at_sender=True)
        return
    if not time.isdigit() and '*' not in time:
        await bot.send(ev, '时长？？？')
    else:
        if uid == sid or priv.check_priv(ev,priv.ADMIN):
            try:
                await bot.set_group_ban(
                    group_id = gid,
                    user_id = sid,
                    duration = eval(time)
                    )
                if time == '0':
                    await bot.send(ev, f'[CQ:at,qq={sid}]的口球已经摘下来啦w')
                else:
                    await bot.send(ev, f'成功禁言[CQ:at,qq={sid}]{eval(time)}秒~')

            except Exception as e:
                await bot.send(ev, '口球失败惹呜呜呜...\n错误代码：{e}', at_sender=True)
        elif uid != sid and not priv.check_priv(ev,priv.ADMIN):
            await bot.send(ev, '只有管理员才可以给别人塞口球哦~', at_sender=True)

#头衔申请
async def title_get(bot, ev, uid, sid, gid, title):
    self_info = await self_member_info(bot, ev, gid)
    if self_info['role'] != 'owner':
        await bot.send(ev, '\n失败了~555', at_sender=True)
        return
    if uid == sid or priv.check_priv(ev,priv.ADMIN):
        try:
            await bot.set_group_special_title(
                group_id = gid,
                user_id = sid,
                special_title = title,
                duration = -1
                )
            if not title:
                await bot.send(ev, f'祝贺[CQ:at,qq={sid}]得到没有头衔的头衔~')
            else:
                await bot.send(ev, f'已为[CQ:at,qq={sid}]发放专属头衔“{title}”~')
        except Exception as e:
            await bot.send(ev, f'诶...头衔呢？\n错误代码：{e}', at_sender=True)
    elif uid != sid and not priv.check_priv(ev,priv.ADMIN):
        await bot.send(ev, '只有管理员才可以对别人的头衔进行操作哦~', at_sender=True)

#群组踢人
async def member_kick(bot, ev, uid, sid, gid, is_reject):
    self_info = await self_member_info(bot, ev, gid)
    if self_info['role'] != 'owner' and self_info['role'] != 'admin':
        await bot.send(ev, '\n我需要管理权限', at_sender=True)
        return
    if uid == sid or priv.check_priv(ev,priv.ADMIN):
        try:
            await bot.set_group_kick(
                group_id = gid,
                user_id = sid,
                reject_add_request = is_reject
            )
            await bot.send(ev, f'恭喜幸运用户[CQ:at,qq={sid}]芜湖~')
        except Exception as e:
            await bot.send(ev, f'诶！！！为什么没踢成功！\n错误代码：{e}', at_sender=True)
    elif uid != sid and not priv.check_priv(ev,priv.ADMIN):
        await bot.send(ev, '只有管理才能送飞机票的说', at_sender=True)

#群名片修改
async def card_edit(bot, ev, uid, sid, gid, card_text):
    self_info = await self_member_info(bot, ev, gid)
    if self_info['role'] != 'owner' and self_info['role'] != 'admin':
        await bot.send(ev, '\n我需要管理权限', at_sender=True)
    if uid == sid or priv.check_priv(ev,priv.ADMIN):
        try:
            await bot.set_group_card(
                group_id = gid,
                user_id = sid,
                card = card_text
            )
            await bot.send(ev, f'已经把[CQ:at,qq={sid}]的群名片修改为“{card_text}”啦~')
        except Exception as e:
            await bot.send(ev, f'修改群名片失败勒...\n错误代码：{e}', at_sender=True)
    elif uid != sid and not priv.check_priv(ev,priv.ADMIN):
        await bot.send(ev, '只有管理才能给别人设置名片了啦！', at_sender=True)

		
#群名修改
async def group_name(bot, ev, gid, name):
    self_info = await self_member_info(bot, ev, gid)
    if self_info['role'] != 'owner' and self_info['role'] != 'admin':
        await bot.send(ev, '\n我还没获得管理权限呢...', at_sender=True)
        return    
    if not priv.check_priv(ev,priv.ADMIN):
        await bot.send(ev, '才不听你的~变态ヽ(*。>Д<)o゜', at_sender=True) 
    else:   
        try:
            await bot.set_group_name(
			    group_id = gid,
			    group_name = name
			)
            await bot.send(ev, f'群名已修改为“{name}”啦')
        except Exception as e:
            await bot.send(ev, '群名修改失败惹...\n错误代码：{e}', at_sender=True)

#发群公告
async def group_notice(bot, ev, gid, text):
    self_info = await self_member_info(bot, ev, gid)
    if self_info['role'] != 'owner' and self_info['role'] != 'admin':
        await bot.send(ev, '\n我还没获得管理权限呢...', at_sender=True)
        return    
    if not priv.check_priv(ev,priv.ADMIN):
        await bot.send(ev, '才不听你的~变态ヽ(*。>Д<)o゜', at_sender=True) 
    else:   
        try:
            await bot._send_group_notice(
			    group_id = gid,
			    content = text
			)
            await bot.send(ev, f'发送公告完成')
        except Exception as e:
            await bot.send(ev, '公告发送失败惹...\n错误代码：{e}', at_sender=True)  

#管理设置
async def admin_set(bot, ev, sid, gid, status):
    self_info = await self_member_info(bot, ev, gid)
    if self_info['role'] != 'owner':
        await bot.send(ev, '我必须要当群主才行o(╥﹏╥)o', at_sender=True)
        return
    if not priv.check_priv(ev,priv.ADMIN):
        await bot.send(ev, '才不听你的~哼╭(╯^╰)╮', at_sender=True) 
        return
    else: 
        try:
            for m in ev.message:
                await bot.set_group_admin(
                    group_id= gid, 
                    user_id= sid, 
                    enable= status
                )
            if not status:
                await bot.send(ev, f'[CQ:at,qq={sid}]已经成为成员啦~')
            else:
                await bot.send(ev, f'[CQ:at,qq={sid}]已经成为管理啦~')
        except Exception as e:
            await bot.send(ev, f'诶！！！为什么设置成功！\n错误代码：{e}', at_sender=True)