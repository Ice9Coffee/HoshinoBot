from nonebot import on_command, CommandSession
from nonebot import permission as perm
from nonebot.argparse import ArgumentParser

async def ls_group(session: CommandSession):
    gl = await session.bot.get_group_list()
    msg = [ "{group_id} {group_name}".format_map(g) for g in gl ]
    msg = "\n".join(msg)
    msg = "| 群号 | 群名 |\n" + msg
    await session.send(msg)


async def ls_friend(session: CommandSession):
    gl = await session.bot.get_friend_list()
    msg = [ "{user_id} {nickname}".format_map(g) for g in gl ]
    msg = "\n".join(msg)
    msg = "| QQ号 | 昵称 |\n" + msg
    await session.send(msg)


@on_command('ls', permission=perm.SUPERUSER, shell_like=True)
async def ls(session: CommandSession):
    parser = ArgumentParser(session=session)
    switch = parser.add_mutually_exclusive_group()
    switch.add_argument('-g', '--group', action='store_true')
    switch.add_argument('-f', '--friend', action='store_true')
    args = parser.parse_args(session.argv)

    if args.group:
        await ls_group(session)
    elif args.friend:
        await ls_friend(session)

