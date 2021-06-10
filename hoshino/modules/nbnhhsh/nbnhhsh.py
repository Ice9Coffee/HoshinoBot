from hoshino import Service, priv
import aiohttp

sv_help = '''
[? XX] XX是你不理解的dx
'''.strip()

sv = Service(
    name='好好说话',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 是否可见
    enable_on_default=True,  # 是否默认启用
    bundle='通用',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助-好好说话"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


@sv.on_rex(r'^[\?\？]{1,2} ?([a-z0-9]+)$', normalize=True)
async def hhsh(bot, event):
    match = event['match']
    async with aiohttp.TCPConnector(verify_ssl=False) as connector:
        async with aiohttp.request(
                'POST',
                url='https://lab.magiconch.com/api/nbnhhsh/guess',
                json={"text": match.group(1)},
                connector=connector,
        ) as resp:
            j = await resp.json()
    if len(j) == 0:
        await bot.send(event, '没有结果', at_sender=True)
        return
    res = j[0]
    name = res.get('name')
    trans = res.get('trans', '没有结果')
    msg = '{}: {}'.format(
        name,
        ' '.join(trans),
    )
    await bot.send(event, msg, at_sender=True)
