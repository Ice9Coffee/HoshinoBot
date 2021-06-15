from hoshino import Service, priv
from hoshino.typing import CQEvent

sv = Service('_help_', manage_priv=priv.SUPERUSER, visible=False)

TOP_MANUAL = '''
====================
= HoshinoBot使用说明 =
====================
发送[]内的关键词触发

====== 常用指令 ======
[启用会战] 选择会战版本
[怎么拆日和] 竞技场查询
[星乃来发十连] 转蛋模拟
[星乃来一井] 转蛋井模拟
[pcr速查] 常用网址
[官漫132] 四格漫画(日)
[切噜一下+待加密文本]
  切噜语转换
[来杯咖啡+反馈内容]
  联系维护组

==== 查看更多功能 ====
[帮助pcr会战][帮助pcr查询]
[帮助pcr娱乐][帮助pcr订阅]
[帮助artist][帮助kancolle]
[帮助umamusume][帮助通用]

※群管理可控制开关功能※
[lssv] 查看模块的开关状态
[启用+空格+service]
[禁用+空格+service]
=====================
※bot开源项目：
github.com/Ice-Cirno/HoshinoBot
※您的支持是本bot更新维护的动力
'''.strip()

def gen_bundle_manual(bundle_name, service_list, gid):
    manual = [bundle_name]
    service_list = sorted(service_list, key=lambda s: s.name)
    for sv in service_list:
        if sv.visible:
            spit_line = '=' * max(0, 18 - len(sv.name))
            manual.append(f"|{'○' if sv.check_enabled(gid) else '×'}| {sv.name} {spit_line}")
            if sv.help:
                manual.append(sv.help)
    return '\n'.join(manual)


@sv.on_prefix('help', '帮助')
async def send_help(bot, ev: CQEvent):
    bundle_name = ev.message.extract_plain_text().strip()
    bundles = Service.get_bundles()
    if not bundle_name:
        await bot.send(ev, TOP_MANUAL)
    elif bundle_name in bundles:
        msg = gen_bundle_manual(bundle_name, bundles[bundle_name], ev.group_id)
        await bot.send(ev, msg)
    # else: ignore
