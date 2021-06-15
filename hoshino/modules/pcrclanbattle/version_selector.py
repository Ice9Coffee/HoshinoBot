from hoshino import Service, priv
from hoshino.typing import CQEvent

sv = Service('clanbattle-version-selector', manage_priv=priv.SUPERUSER, visible=False)

help_str = '''
请*群管理*或*群主*发送【】内的命令
【启用会战v2】
Hoshino开源版 命令以感叹号开头
适用于2021年6月前的日服、2021年10月前的台服、2023年6月前的B服

【启用会战v3】
指令简化版 无web面板
适用于2021年6月前的日服、2021年10月前的台服、2023年6月前的B服

【启用会战v4】
适用于2021年7月后的日服、2021年11月后的台服、2023年7月后的B服
web绝赞开发中
'''.strip()

@sv.on_prefix('会战启用', '启用会战')
async def version_select(bot, ev: CQEvent):
    gid = ev.group_id
    arg = ev.message.extract_plain_text()
    svs = Service.get_loaded_services()
    cbsvs = {
        'v2': svs.get('clanbattle'),
        'v3': svs.get('clanbattlev3'),
        'v4': svs.get('clanbattlev4'),
    }
    if arg not in cbsvs:
        await bot.finish(ev, help_str)
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有*群管理*和*群主*才能切换会战管理版本')
    if not cbsvs[arg]:
        await bot.finish(ev, f'本bot未实装clanbattle{arg}，请加入Hoshinoのお茶会(787493356)体验！')
    for k, v in cbsvs.items():
        v.set_enable(gid) if k == arg else v.set_disable(gid)
    await bot.send(ev, f'已启用clanbattle{arg}\n{cbsvs[arg].help}')
