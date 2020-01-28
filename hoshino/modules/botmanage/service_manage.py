from nonebot import on_command, CommandSession 
from nonebot import permission as perm 
from nonebot import CQHttpError

from hoshino.service import Service

@on_command('lssv', aliases=('查看所有服务', '查看所有功能', '功能', '功能列表', '服务列表', '菜单'), permission=perm.GROUP, only_to_me=False)
async def lssv(session:CommandSession):
    group_id = session.ctx['group_id']
    all_service = '\n'.join([ f"{'on | ' if group_id in sv.enable_group or sv.enable_on_default and group_id not in sv.disable_group else 'off | '} {sv.name}" for sv in Service.get_loaded_services()])
    await session.send(f"服务一览：\n{all_service}")


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
                await session.send(f'权限不足！需要：{sv.manage_priv}，您的：{u_priv}', at_sender=True)
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
                await session.send(f'权限不足！需要：{sv.manage_priv}，您的：{u_priv}', at_sender=True)
                return
    await session.send(f'未找到服务：{target_name}', at_sender=True)
