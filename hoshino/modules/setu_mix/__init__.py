import hoshino
import asyncio
from .base import *
from hoshino import Service, priv
from .config import get_config, get_group_config, set_group_config

sv_help = '''
- [色图/来N张色图] 随机获取1张/n张色图
- [搜N张色图 XX] 搜索XX的色图,附带数量可以获取多张
- [本日涩图排行榜 X ] 获取p站排行榜(需开启acggov模块),X为页数
- [看涩图 X /看涩图 X Y] 获取p站排行榜指定序号色图(需开启acggov模块),从X到Y或者只看X
- [匿名色图] Q群的bots受到不可名状意志的控制(需关闭xml模块)
- [show色图/show来N张色图] 带上show前缀涩图会发生变化(需关闭xml模块)
'''.strip()

sv = Service(
    name='setu_pro',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 是否可见
    enable_on_default=True,  # 是否默认启用
    bundle='通用',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助-setu_pro"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


# 设置limiter
tlmt = hoshino.util.DailyNumberLimiter(get_config('base', 'daily_max'))
flmt = hoshino.util.FreqLimiter(get_config('base', 'freq_limit'))


def check_lmt(uid, num):
    if uid in hoshino.config.SUPERUSERS:
        return 0, ''
    if not tlmt.check(uid):
        return 1, f"您今天已经冲过{get_config('base', 'daily_max')}次了,请明天再来!"
    if num > 1 and (get_config('base', 'daily_max') - tlmt.get_num(uid)) < num:
        return 1, f"您今天的剩余次数为{get_config('base', 'daily_max') - tlmt.get_num(uid)}次,已不足{num}次,请节制!"
    if not flmt.check(uid):
        return 1, f'您冲的太快了,请等待{round(flmt.left_time(uid))}秒!'
    # tlmt.increase(uid,num)
    flmt.start_cd(uid)
    return 0, ''


@sv.on_prefix('setu')
async def send_setu(bot, ev):
    uid = ev['user_id']
    gid = ev['group_id']
    is_su = hoshino.priv.check_priv(ev, hoshino.priv.SUPERUSER)
    args = ev.message.extract_plain_text().split()

    msg = ''
    if not is_su:
        msg = '需要超级用户权限'
    elif len(args) == 0:
        msg = 'invalid parameter'
    elif args[0] == 'set' and len(args) >= 3:  # setu set module on [group]
        if len(args) >= 4 and args[3].isdigit():
            gid = int(args[3])
        key = None
        value = False
        if args[1] == 'lolicon':
            key = 'lolicon'
        elif args[1] == 'lolicon_r18':
            key = 'lolicon_r18'
        elif args[1] == 'acggov':
            key = 'acggov'
        elif args[1] == 'withdraw':
            key = 'withdraw'
        elif args[1] == 'xml':
            key = 'xml'
        if args[2] == 'on' or args[2] == 'true':
            value = True
        elif args[2] == 'off' or args[2] == 'false':
            value = False
        elif args[2].isdigit():
            value = int(args[2])
        if key:
            set_group_config(gid, key, value)
            msg = f'{gid} : {key} = {value}'
        else:
            msg = 'invalid parameter'
    elif args[0] == 'get':
        if len(args) >= 2 and args[1].isdigit():
            gid = int(args[1])
        msg = f'group {gid} :'
        msg += f'\nwithdraw : {get_group_config(gid, "withdraw")}'
        msg += f'\nxml : {get_group_config(gid, "xml")}'
        msg += f'\nlolicon : {get_group_config(gid, "lolicon")}'
        msg += f'\nlolicon_r18 : {get_group_config(gid, "lolicon_r18")}'
        msg += f'\nacggov : {get_group_config(gid, "acggov")}'
    elif args[0] == 'fetch':
        await bot.send(ev, 'start fetch mission')
        await fetch_process()
        msg = 'fetch mission complete'
    elif args[0] == 'warehouse':
        msg = 'warehouse:'
        state = check_path()
        for k, v in state.items():
            msg += f'\n{k} : {v}'
    else:
        msg = 'invalid parameter'
    await bot.send(ev, msg)


@sv.on_rex(r'^不够[涩瑟色]|^再来[点张份]|^[涩瑟色]图$|^[再]?来?(\d*)?[份点张]([涩色瑟]图)')
async def send_random_setu(bot, ev):
    num = 1
    match = ev['match']
    try:
        num = int(match.group(1))
    except:
        pass
    uid = ev['user_id']
    gid = ev['group_id']
    result, msg = check_lmt(uid, num)
    if result != 0:
        await bot.send(ev, msg)
        return

    result_list = []
    for _ in range(num):
        msg = await get_setu(gid)
        if msg == None:
            await bot.send(ev, '无可用模块')
            return
        try:
            result_list.append(await bot.send(ev, msg))
        except:
            print('图片发送失败')
        await asyncio.sleep(1)

    tlmt.increase(uid, len(result_list))

    second = get_group_config(gid, "withdraw")
    if second and second > 0:
        await asyncio.sleep(second)
        for result in result_list:
            try:
                await bot.delete_msg(self_id=ev['self_id'], message_id=result['message_id'])
            except:
                print('撤回失败')
            await asyncio.sleep(1)


@sv.on_rex(r'^show不够[涩瑟色]|^show再来[点张份]|^show[涩瑟色]图$|^show[再]?来?(\d*)?[份点张]([涩色瑟]图)')
async def send_random_setu(bot, ev):
    num = 1
    match = ev['match']
    try:
        num = int(match.group(1))
    except:
        pass
    uid = ev['user_id']
    gid = ev['group_id']
    result, msg = check_lmt(uid, num)
    if result != 0:
        await bot.send(ev, msg)
        return

    result_list = []
    for _ in range(num):
        msg = await get_setu2(gid)
        if msg == None:
            await bot.send(ev, '无可用模块')
            return
        try:
            result_list.append(await bot.send(ev, msg))
        except:
            print('图片发送失败')
        await asyncio.sleep(1)

    tlmt.increase(uid, len(result_list))

    second = get_group_config(gid, "withdraw")
    if second and second > 0:
        await asyncio.sleep(second)
        for result in result_list:
            try:
                await bot.delete_msg(self_id=ev['self_id'], message_id=result['message_id'])
            except:
                print('撤回失败')
            await asyncio.sleep(1)


@sv.on_rex(r'^搜[索]?(\d*)[份张]*(.*?)[涩瑟色]图(.*)')
async def send_search_setu(bot, ev):
    uid = ev['user_id']
    gid = ev['group_id']

    keyword = ev['match'].group(2) or ev['match'].group(3)
    if not keyword:
        await bot.send(ev, '需要提供关键字')
        return
    keyword = keyword.strip()
    num = ev['match'].group(1)
    if num:
        num = int(num.strip())
    else:
        num = 1
    result, msg = check_lmt(uid, num)
    if result != 0:
        await bot.send(ev, msg)
        return

    await bot.send(ev, '正在搜索...')
    msg_list = await search_setu(gid, keyword, num)
    if len(msg_list) == 0:
        await bot.send(ev, '无结果')
    result_list = []
    for msg in msg_list:
        try:
            result_list.append(await bot.send(ev, msg))
        except:
            print('图片发送失败')
        await asyncio.sleep(1)
    tlmt.increase(uid, len(result_list))
    second = get_group_config(gid, "withdraw")
    if second and second > 0:
        await asyncio.sleep(second)
        for result in result_list:
            try:
                await bot.delete_msg(self_id=ev['self_id'], message_id=result['message_id'])
            except:
                print('撤回失败')
            await asyncio.sleep(1)


@sv.on_rex(r'([本每]日)?[涩色瑟]图排行榜\D*(\d*)')
async def send_ranking(bot, ev):
    gid = ev['group_id']
    page = ev['match'].group(2)
    if page and page.isdigit():
        page = int(page)
        page -= 1
    else:
        page = 0
    if page < 0:
        page = 0
    msg = await get_ranking(gid, page)
    if msg == None:
        msg = '模块未启用'
    await bot.send(ev, msg)


@sv.on_prefix(('看涩图', '看色图', '看瑟图'))
async def send_ranking_setu(bot, ev):
    uid = ev['user_id']
    gid = ev['group_id']
    start = 0
    end = 0
    args = ev.message.extract_plain_text().split()
    if len(args) > 0 and args[0].isdigit():
        start = int(args[0])
        start -= 1
        if start < 0:
            start = 0
        end = start + 1
    if len(args) > 1 and args[1].isdigit():
        end = int(args[1])
    result, msg = check_lmt(uid, end - start)
    if result != 0:
        await bot.send(ev, msg)
        return
    result_list = []
    for i in range(start, end):
        msg = await get_ranking_setu(gid, i)
        if msg == None:
            await bot.send(ev, '模块未启用')
            return
        try:
            result_list.append(await bot.send(ev, msg))
        except:
            print('图片发送失败')
        await asyncio.sleep(1)
    tlmt.increase(uid, len(result_list))
    second = get_group_config(gid, "withdraw")
    if second and second > 0:
        await asyncio.sleep(second)
        for result in result_list:
            try:
                await bot.delete_msg(self_id=ev['self_id'], message_id=result['message_id'])
            except:
                print('撤回失败')
            await asyncio.sleep(1)


@sv.on_prefix("匿名色图")
async def send_random_setu(bot, ev):
    uid = ev['user_id']
    gid = ev['group_id']
    data_all = []
    text1 = await get_setu1(gid)
    text2 = await get_setu1(gid)
    text3 = await get_setu1(gid)
    text4 = await get_setu1(gid)
    text5 = await get_setu1(gid)
    text6 = await get_setu1(gid)
    text7 = await get_setu1(gid)
    text8 = await get_setu1(gid)
    text9 = await get_setu1(gid)
    data1 = {
        "type": "node",
        "data": {
            "name": 'Q群涩图管家',
            "uin": '2854196310',
            "content": text1
        }
    }
    data2 = {
        "type": "node",
        "data": {
            "name": '好色的小冰',
            "uin": '2854196306',
            "content": text2
        }
    }
    data3 = {
        "type": "node",
        "data": {
            "name": '涩图豆',
            "uin": '2854196314',
            "content": text3
        }
    }
    data4 = {
        "type": "node",
        "data": {
            "name": 'Q群官方色图',
            "uin": '2854196320',
            "content": text4
        }
    }
    data5 = {
        "type": "node",
        "data": {
            "name": 'QQ涩图惠购',
            "uin": '2854196925',
            "content": text5
        }
    }
    data6 = {
        "type": "node",
        "data": {
            "name": '涩图图',
            "uin": '2854200117',
            "content": text6
        }
    }
    data7 = {
        "type": "node",
        "data": {
            "name": '涩小狐',
            "uin": '2854196311',
            "content": text7
        }
    }
    data8 = {
        "type": "node",
        "data": {
            "name": '涩图老铁',
            "uin": '2854196312',
            "content": text8
        }
    }
    data9 = {
        "type": "node",
        "data": {
            "name": '堕落星妹',
            "uin": '2854214267',
            "content": text9
        }
    }
    data_all = [data1, data2, data3, data4, data5, data6, data7, data8, data9]
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=data_all)


@sv.on_prefix("show匿名色图")
async def send_random_setu(bot, ev):
    uid = ev['user_id']
    gid = ev['group_id']
    data_all = []
    text1 = await get_setu2(gid)
    text2 = await get_setu2(gid)
    text3 = await get_setu2(gid)
    text4 = await get_setu2(gid)
    text5 = await get_setu2(gid)
    text6 = await get_setu2(gid)
    text7 = await get_setu2(gid)
    text8 = await get_setu2(gid)
    text9 = await get_setu2(gid)
    data1 = {
        "type": "node",
        "data": {
            "name": 'Q群涩图管家',
            "uin": '2854196310',
            "content": text1
        }
    }
    data2 = {
        "type": "node",
        "data": {
            "name": '好色的小冰',
            "uin": '2854196306',
            "content": text2
        }
    }
    data3 = {
        "type": "node",
        "data": {
            "name": '涩图豆',
            "uin": '2854196314',
            "content": text3
        }
    }
    data4 = {
        "type": "node",
        "data": {
            "name": 'Q群官方色图',
            "uin": '2854196320',
            "content": text4
        }
    }
    data5 = {
        "type": "node",
        "data": {
            "name": 'QQ涩图惠购',
            "uin": '2854196925',
            "content": text5
        }
    }
    data6 = {
        "type": "node",
        "data": {
            "name": '涩图图',
            "uin": '2854200117',
            "content": text6
        }
    }
    data7 = {
        "type": "node",
        "data": {
            "name": '涩小狐',
            "uin": '2854196311',
            "content": text7
        }
    }
    data8 = {
        "type": "node",
        "data": {
            "name": '涩图老铁',
            "uin": '2854196312',
            "content": text8
        }
    }
    data9 = {
        "type": "node",
        "data": {
            "name": '堕落星妹',
            "uin": '2854214267',
            "content": text9
        }
    }
    data_all = [data1, data2, data3, data4, data5, data6, data7, data8, data9]
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=data_all)


@sv.scheduled_job('interval', minutes=30)
async def job():
    await fetch_process()
