from service import Service,Priv
import re

import os

config_path = os.path.dirname(__file__)+'/config.json'
_sv = Service('服务管理',config_path,default_enable=True)
@_sv.on_message()
async def manage(bot,ctx):
    message = ctx['message'].extract_plain_text().strip()
    gid = ctx.get('group_id',0)
    uid = ctx['user_id']
    user_priv = _sv.get_user_priv(ctx)
    svs = _sv.get_loaded_services()
    if message == '查看已开启服务' or message=='ls':
        group_svs = get_group_services(ctx)
        reply = show_services(group_svs,'本群已开启服务')
        await bot.send(ctx,reply,at_sender=False)
        return

    if message == '查看所有服务' or message == 'ls -a':
        reply = show_services(svs,'所有服务')
        await bot.send(ctx,reply,at_sender=False)
        return

    if re.match('start.{1,10}',message):
        sv_name = message[5:].strip()
        if sv_name in svs:
            if svs[sv_name].set_enable(ctx):
                await bot.send(ctx,f'{sv_name}已开启',at_sender=True)
            else:
                await bot.send(ctx,f'权限不足，开启该服务需要主人权限',at_sender=True)
        return

    if re.match('stop.{1,10}',message):
        sv_name = message[4:].strip()
        if sv_name in svs:
            if svs[sv_name].set_disable(ctx):
                await bot.send(ctx,f'{sv_name}已停用',at_sender=True)
            else:
                await bot.send(ctx,f'权限不足，停用该服务需要主人权限',at_sender=True)
        return

    if re.match('群?(\d{7,10})?禁用(.{1,10})',message):
        obj = re.match('群?(\d{7,10})?禁用(.{1,10})',message)
        try:
            gid_to_disable = int(obj.group(1))
        except:
            gid_to_disable = None
        sv_name = obj.group(2)
        if gid_to_disable and _sv.get_user_priv(ctx) < Priv.SUPER:
            await bot.send(ctx,'权限不足',at_sender=True)
            return 
        if not gid_to_disable:
            gid_to_disable = gid
        if sv_name in svs:
            if svs[sv_name].add_disable_group(gid_to_disable,ctx):
                await bot.send(ctx,f'成功禁用群{gid_to_disable}{sv_name}服务',at_sender=True)
            else:
                await bot.send(ctx,f'权限不足，禁用该服务需要权限大于{svs[sv_name].manage_priv}',at_sender=True)
        else:
            await bot.send(ctx,f'未找到该服务',at_sender=True)
        return

    if re.match('群?(\d{7,10})?启用(.{1,10})',message):
        obj = re.match('群?(\d{7,10})?启用(.{1,10})',message)
        try:
            gid_to_enable = int(obj.group(1))
        except:
            gid_to_enable = None
        sv_name = obj.group(2)
        if gid_to_enable and _sv.get_user_priv(ctx) < Priv.SUPER:
            await bot.send(ctx,'权限不足',at_sender=True)
            return 
        if not gid_to_enable:
            gid_to_enable = gid
        if sv_name in svs:
            if svs[sv_name].add_enable_group(gid_to_enable,ctx):
                await bot.send(ctx,f'成功启用群{gid_to_enable}{sv_name}服务',at_sender=True)
            else:
                await bot.send(ctx,f'权限不足，启用该服务需要权限大于{svs[sv_name].manage_priv}',at_sender=True)
        else:
            await bot.send(ctx,f'未找到该服务',at_sender=True)
        return

    
        

def get_group_services(ctx):
    svs = _sv.get_loaded_services()
    group_svs = {}
    for key in svs:
        if  svs[key].check_group(ctx):
            group_svs[key] = svs[key]
    return group_svs

def show_services(svs,head):
    reply = f'{head}:\n\n'
    for key in svs:
        if not svs[key].is_visible:
            continue
        reply += f'{svs[key].name}\n'
    reply = reply.strip()
    return reply


