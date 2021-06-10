from .nmsl_local import *

from hoshino import Service, priv

sv_help = '''
- [抽象一下 XX] 将XX转换为抽象话
- [我佛辣 XX] 将XX转换为深度抽象话
'''.strip()

sv = Service(
    name='抽象话',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 是否可见
    enable_on_default=True,  # 是否默认启用
    bundle='娱乐',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助-抽象话"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


@sv.on_prefix(('抽象一下', '轻度抽象'))
async def emoji(bot, ev):
    text = ev.message.extract_plain_text()
    msg = text_to_emoji(text, method=0)
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(('我佛辣', '深度抽象'))
async def nmsl(bot, ev):
    text = ev.message.extract_plain_text()
    msg = text_to_emoji(text, method=1)
    await bot.send(ev, msg, at_sender=True)
