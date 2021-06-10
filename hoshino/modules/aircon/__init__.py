import datetime
from .airconutils import get_group_aircon, write_group_aircon, update_aircon, new_aircon, print_aircon
from hoshino import Service, priv

try:
    import ujson as json
except:
    import json

sv = Service(
    name='群空调',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # False隐藏
    enable_on_default=True,  # 是否默认启用
    bundle='通用',  # 属于哪一类
)

ac_type_text = ["私人空调", "中央空调"]
AIRCON_HOME = 0
AIRCON_CENTRAL = 1

aircons = get_group_aircon(__file__)


async def check_status(gid, bot, event, need_on=True):
    if gid not in aircons:
        await bot.send(event, "空调还没装哦~发送“开空调”安装空调")
        return None

    aircon = aircons[gid]
    if need_on and not aircon["is_on"]:
        await bot.send(event, "💤你空调没开！")
        return None

    return aircon


async def check_range(bot, event, low, high, errormsg, special=None):
    msg = event.message.extract_plain_text().split()

    if special is not None and msg[0] in special:
        return special[msg[0]]

    try:
        val = int(msg[0])
    except:
        await bot.send(event, f"⚠️输入有误！只能输入{low}至{high}的整数")
        return None

    if not low <= val <= high:
        await bot.send(event, errormsg)
        return None

    return val


@sv.on_fullmatch('开空调')
async def aircon_on(bot, event):
    gid = str(event['group_id'])

    if gid not in aircons:
        ginfo = await bot.get_group_info(group_id=gid)
        gcount = ginfo["member_count"]
        aircon = new_aircon(num_member=gcount)
        aircons[gid] = aircon
        await bot.send(event, "❄空调已安装~")
    else:
        aircon = aircons[gid]
        if aircon["is_on"]:
            await bot.send(event, "❄空调开着呢！")
            return

    update_aircon(aircon)
    aircon['is_on'] = True
    msg = print_aircon(aircon)
    write_group_aircon(__file__, aircons)
    await bot.send(event, "❄哔~空调已开\n" + msg)


@sv.on_fullmatch('关空调')
async def aircon_off(bot, event):
    gid = str(event['group_id'])

    aircon = await check_status(gid, bot, event)
    if aircon is None:
        return

    update_aircon(aircon)
    aircon['is_on'] = False
    msg = print_aircon(aircon)
    write_group_aircon(__file__, aircons)
    await bot.send(event, '💤哔~空调已关\n' + msg)


@sv.on_fullmatch('当前温度')
async def aircon_now(bot, event):
    gid = str(event['group_id'])

    aircon = await check_status(gid, bot, event, need_on=False)
    if aircon is None:
        return

    aircon = aircons[gid]
    update_aircon(aircon)
    msg = print_aircon(aircon)
    write_group_aircon(__file__, aircons)

    if not aircon["is_on"]:
        msg = "💤空调未开启\n" + msg
    else:
        msg = "❄" + msg

    await bot.send(event, msg)


@sv.on_prefix(('设置温度', '设定温度'))
async def set_temp(bot, event):
    gid = str(event['group_id'])

    aircon = await check_status(gid, bot, event)
    if aircon is None:
        return

    set_temp = await check_range(bot, event, -273, 999999, "只能设置-273-999999°C喔")
    if set_temp is None:
        return

    if set_temp == 114514:
        await bot.send(event, "这么臭的空调有什么装的必要吗")
        return

    update_aircon(aircon)
    aircon["set_temp"] = set_temp
    msg = print_aircon(aircon)
    write_group_aircon(__file__, aircons)
    await bot.send(event, "❄" + msg)


@sv.on_prefix(('设置风速', '设定风速', '设置风量', '设定风量'))
async def set_wind_rate(bot, event):
    gid = str(event['group_id'])

    aircon = await check_status(gid, bot, event)
    if aircon is None:
        return

    if aircon["ac_type"] != AIRCON_HOME:
        await bot.send(event, "只有家用空调能调风量哦！")
        return

    wind_rate = await check_range(bot, event, 1, 3, "只能设置1/2/3档喔",
                                  {"低": 1, "中": 2, "高": 3})
    if wind_rate is None:
        return

    update_aircon(aircon)
    aircon["wind_rate"] = wind_rate - 1
    msg = print_aircon(aircon)
    write_group_aircon(__file__, aircons)
    await bot.send(event, "❄" + msg)


@sv.on_prefix(('设置环境温度', '设定环境温度'))
async def set_env_temp(bot, event):
    gid = str(event['group_id'])

    aircon = await check_status(gid, bot, event, need_on=False)
    if aircon is None:
        return

    env_temp = await check_range(bot, event, -273, 999999, "只能设置-273-999999°C喔")
    if env_temp is None:
        return

    if env_temp == 114514:
        await bot.send(event, "这么臭的空调有什么装的必要吗")
        return

    aircon = aircons[gid]
    update_aircon(aircon)
    aircon["env_temp"] = env_temp
    msg = print_aircon(aircon)
    write_group_aircon(__file__, aircons)

    if not aircon["is_on"]:
        msg = "💤空调未开启\n" + msg
    else:
        msg = "❄" + msg

    await bot.send(event, msg)


@sv.on_fullmatch(('空调类型',))
async def show_aircon_type(bot, event):
    gid = str(event['group_id'])

    aircon = await check_status(gid, bot, event, need_on=False)
    if aircon is None:
        return

    aircon = aircons[gid]
    ac_type = aircon["ac_type"]

    msg = f"当前安装了{ac_type_text[ac_type]}哦~"
    await bot.send(event, msg)


@sv.on_fullmatch(('升级空调', '空调升级'))
async def upgrade_aircon(bot, event):
    gid = str(event['group_id'])

    aircon = await check_status(gid, bot, event, need_on=False)
    if aircon is None:
        return

    aircon = aircons[gid]
    ac_type = aircon["ac_type"]
    if ac_type == len(ac_type_text) - 1:
        await bot.send(event, "已经是最高级的空调啦！")
        return

    update_aircon(aircon)
    ac_type += 1
    aircon["ac_type"] = ac_type
    msg = print_aircon(aircon)
    write_group_aircon(__file__, aircons)
    msg = f"❄已升级至{ac_type_text[ac_type]}~\n" + msg
    await bot.send(event, msg)


@sv.on_fullmatch(('降级空调', '空调降级'))
async def downgrade_aircon(bot, event):
    gid = str(event['group_id'])

    aircon = await check_status(gid, bot, event, need_on=False)
    if aircon is None:
        return

    aircon = aircons[gid]
    ac_type = aircon["ac_type"]
    if ac_type == 0:
        await bot.send(event, "已经是最基础级别的空调啦！")
        return

    update_aircon(aircon)
    ac_type -= 1
    aircon["ac_type"] = ac_type
    msg = print_aircon(aircon)
    write_group_aircon(__file__, aircons)
    msg = f"❄已降级至{ac_type_text[ac_type]}~\n" + msg
    await bot.send(event, msg)
