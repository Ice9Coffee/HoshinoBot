from nonebot import on_command, CommandSession 
from nonebot import permission as perm 
from nonebot import CQHttpError

from hoshino.service import Service


@on_command('enable', aliases=('启用', '开启', '打开'), permission=perm.GROUP, only_to_me=False)
async def enable_service(session:CommandSession):
    if session.ctx['message_type'] != 'group':
        return
    all_service = Service.get_loaded_services()
    target_name = session.current_arg
    for sv in all_service:
        if sv.name == target_name:
            if await sv.check_permission(session.ctx, sv.manage_priv):
                sv.set_enable(session.ctx['group_id'])
                session.send(f'{sv.name}服务已启用！', at_sender=True)
                return
            else:
                session.send('权限不足', at_sender=True)
                return
    session.send(f'未找到服务：{target_name}', at_sender=True)


@on_command('disable', aliases=('禁用', '关闭'), permission=perm.GROUP, only_to_me=False)
async def disable_service(session:CommandSession):
    if session.ctx['message_type'] != 'group':
        return
    all_service = Service.get_loaded_services()
    target_name = session.current_arg
    for sv in all_service:
        if sv.name == target_name:
            if await sv.check_permission(session.ctx, sv.manage_priv):
                sv.set_disable(session.ctx['group_id'])
                session.send(f'{sv.name}服务已禁用！', at_sender=True)
                return
            else:
                session.send('权限不足', at_sender=True)
                return
    session.send(f'未找到服务：{target_name}', at_sender=True)
