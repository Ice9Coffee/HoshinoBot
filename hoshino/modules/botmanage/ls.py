from nonebot.argparse import ArgumentParser
from hoshino import Service, sucmd
from hoshino.typing import CommandSession


async def ls_group(session: CommandSession):
    bot = session.bot
    self_ids = bot.get_self_ids()
    for sid in self_ids:
        gl = await bot.get_group_list(self_id=sid)
        msg = [ "{group_id} {group_name}".format_map(g) for g in gl ]
        msg = "\n".join(msg)
        msg = f"bot:{sid}\n| 群号 | 群名 | 共{len(gl)}个群\n" + msg
        await bot.send_private_msg(self_id=sid, user_id=bot.config.SUPERUSERS[0], message=msg)


async def ls_friend(session: CommandSession):
    gl = await session.bot.get_friend_list(self_id=session.event.self_id)
    msg = [ "{user_id} {nickname}".format_map(g) for g in gl ]
    msg = "\n".join(msg)
    msg = f"| QQ号 | 昵称 | 共{len(gl)}个好友\n" + msg
    await session.send(msg)


async def ls_service(session: CommandSession, service_name: str):
    all_services = Service.get_loaded_services()
    if service_name in all_services:
        sv = all_services[service_name]
        on_g = '\n'.join(map(str, sv.enable_group))
        off_g = '\n'.join(map(str, sv.disable_group))
        default_ = 'enabled' if sv.enable_on_default else 'disabled'
        msg = f"服务{sv.name}：\n默认：{default_}\nuse_priv={sv.use_priv}\nmanage_priv={sv.manage_priv}\nvisible={sv.visible}\n启用群：\n{on_g}\n禁用群：\n{off_g}"
        session.finish(msg)
    else:
        session.finish(f'未找到服务{service_name}')


async def ls_bot(session: CommandSession):
    self_ids = session.bot.get_self_ids()
    await session.send(f"共{len(self_ids)}个bot\n{self_ids}")


@sucmd('ls', shell_like=True)
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
