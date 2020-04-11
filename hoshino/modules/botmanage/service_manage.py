from functools import cmp_to_key

from nonebot import on_command, CommandSession 
from nonebot import permission as perm 
from nonebot import CQHttpError

from hoshino.service import Service

PRIV_NOTE = '群主=22 群管=21 群员=0 bot维护组=999'

@on_command('lssv', aliases=('查看所有服务', '查看所有功能', '功能', '功能列表', '服务列表', '菜单'), permission=perm.GROUP_ADMIN, only_to_me=False)
async def lssv(session:CommandSession):
    verbose_all = session.current_arg_text == '-a' or session.current_arg_text == '--all'
    gid = session.ctx['group_id']
    msg = ["服务一览："]
    svs = Service.get_loaded_services()
    svs = map(lambda sv: (sv, sv.check_enabled(gid)), svs)
    key = cmp_to_key(lambda x, y: (y[1] - x[1]) or (-1 if x[0].name < y[0].name else 1 if x[0].name > y[0].name else 0))
    svs = sorted(svs, key=key)
    for sv, on in svs:
        if sv.visible or verbose_all:
            x = '○' if on else '×'
            msg.append(f"|{x}| {sv.name}")
    await session.send('\n'.join(msg))


@on_command('enable', aliases=('启用', '开启', '打开'), permission=perm.GROUP, only_to_me=False)
async def enable_service(session:CommandSession):
    if session.ctx['message_type'] != 'group':
        return
    all_service = Service.get_loaded_services()
    target_name = session.current_arg
    for sv in all_service:
        if sv.name == target_name:
            u_priv = await sv.get_user_privilege(session.ctx)
            if u_priv >= sv.manage_priv:
                sv.set_enable(session.ctx['group_id'])
                await session.send(f'{sv.name}服务已启用！', at_sender=True)
                return
            else:
                await session.send(f'权限不足！需要：{sv.manage_priv}，您的：{u_priv}\n{PRIV_NOTE}', at_sender=True)
                return
    await session.send(f'未找到服务：{target_name}', at_sender=True)


@on_command('disable', aliases=('禁用', '关闭'), permission=perm.GROUP, only_to_me=False)
async def disable_service(session:CommandSession):
    if session.ctx['message_type'] != 'group':
        return
    all_service = Service.get_loaded_services()
    target_name = session.current_arg
    for sv in all_service:
        if sv.name == target_name:
            u_priv = await sv.get_user_privilege(session.ctx)
            if u_priv >= sv.manage_priv:
                sv.set_disable(session.ctx['group_id'])
                await session.send(f'{sv.name}服务已禁用！', at_sender=True)
                return
            else:
                await session.send(f'权限不足！需要：{sv.manage_priv}，您的：{u_priv}\n{PRIV_NOTE}', at_sender=True)
                return
    await session.send(f'未找到服务：{target_name}', at_sender=True)
