from nonebot import on_command, CommandSession
from nonebot import permission as perm
from nonebot.argparse import ArgumentParser

from hoshino.service import Service

async def ls_group(session: CommandSession):
    bot = session.bot
    self_ids = bot._wsr_api_clients.keys()
    for sid in self_ids:
        gl = await bot.get_group_list(self_id=sid)
        msg = [ "{group_id} {group_name}".format_map(g) for g in gl ]
        msg = "\n".join(msg)
        msg = f"bot:{sid}\n| 群号 | 群名 | 共{len(gl)}个群\n" + msg
        await bot.send_private_msg(self_id=sid, user_id=bot.config.SUPERUSERS[0], message=msg)


async def ls_friend(session: CommandSession):
    gl = await session.bot.get_friend_list(self_id=session.ctx['self_id'])
    msg = [ "{user_id} {nickname}".format_map(g) for g in gl ]
    msg = "\n".join(msg)
    msg = f"| QQ号 | 昵称 | 共{len(gl)}个好友\n" + msg
    await session.send(msg)


async def ls_service(session: CommandSession, service_name:str):
    all_services = Service.get_loaded_services()
    for sv in all_services:
        if sv.name == service_name:
            
            on_g = '\n'.join(map(lambda x: str(x), sv.enable_group))
            off_g = '\n'.join(map(lambda x: str(x), sv.disable_group))
            default_ = '开启' if sv.enable_on_default else '关闭'
            msg = f"服务{service_name}：\n默认：{default_}\n启用群：\n{on_g}\n禁用群：\n{off_g}"
            await session.finish(msg)
            return
    await session.send(f'未找到服务{service_name}')


async def ls_bot(session:CommandSession):
    self_ids = session.bot._wsr_api_clients.keys()
    msg = str(self_ids)
    await session.send(msg)


@on_command('ls', permission=perm.SUPERUSER, shell_like=True)
async def ls(session: CommandSession):
    parser = ArgumentParser(session=session)
    switch = parser.add_mutually_exclusive_group()
    switch.add_argument('-g', '--group', action='store_true')
    switch.add_argument('-f', '--friend', action='store_true')
    switch.add_argument('-b', '--bot', action='store_true')
    switch.add_argument('-s', '--service')
    args = parser.parse_args(session.argv)

    if args.group:
        await ls_group(session)
    elif args.friend:
        await ls_friend(session)
    elif args.bot:
        await ls_bot(session)
    elif args.service:
        await ls_service(session, args.service)
