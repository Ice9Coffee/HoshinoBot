from os import path

from lxml import etree
from nonebot import CommandSession
from bilibili_api import live
from hoshino.service import Service, priv
from .._util import load_config, save_config, broadcast, RSS


class Live(RSS):
    def __init__(self, route: str):
        super().__init__()
        self.route = route
        self.latest_time = ''

    def parse_xml(self):
        rss = etree.XML(self.xml)
        items = rss.xpath('/rss/channel/item')
        data = {}
        tuber = rss.xpath('/rss/channel')[0].find('./title').text
        data['tuber'] = tuber
        if items:
            i = items[0]
            data['link'] = i.find('./link').text.strip()
            data['title'] = i.find('./title').text.strip()
            data['latest_time'] = i.find('./pubDate').text.strip()
        return data


class BiliLive(Live):
    def __init__(self, room_id):
        super().__init__(f'/bilibili/live/room/{room_id}')
        self.platform = '哔哩哔哩'
        self.room_id = room_id


class DouyuLive(Live):
    def __init__(self, room_id):
        super().__init__(f'/douyu/room/{room_id}')
        self.platform = '斗鱼'
        self.room_id = room_id


async def notice(room_id, msg):
    groups = _subscribes[str(room_id)]['subs_groups']
    await broadcast(msg, groups=groups)


sv_help = """"""

sv = Service(
    name='直播推送',
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 是否可见
    enable_on_default=True,  # 是否默认启用
    bundle='订阅',  # 属于哪一类
    help_=sv_help  # 帮助文本
)

subs_path = path.join(path.dirname(__file__), 'subs.json')
_subscribes = load_config(subs_path)
_lives = []
for subs in _subscribes:
    platform = _subscribes[subs]['platform']
    room_id = _subscribes[subs]['room']
    latest_time = _subscribes[subs]['latest_time']
    if platform == 'bilibili':
        bl = BiliLive(room_id)
        bl.latest_time = latest_time
        _lives.append(bl)
    elif platform == 'douyu':
        dl = DouyuLive(room_id)
        dl.latest_time = latest_time
        _lives.append(dl)


@sv.scheduled_job('cron', minute='*', second='10')
async def check_live():
    for lv in _lives:
        if lv.platform == '哔哩哔哩':
            await check_bili_live(lv)
        else:
            await check_other_live(lv)


async def check_bili_live(lv):
    roomId = lv.room_id
    data = await live.LiveRoom(room_display_id=roomId).get_room_info()
    roomInfo = data.get('room_info')
    if roomInfo.get('live_status') == 1:  # 开播状态
        title = roomInfo['title']
        cover = roomInfo['cover']
        live_start_time = roomInfo['live_start_time']
        link = "https://live.bilibili.com/" + str(roomId)
        # 判断是否是新开播
        if live_start_time != lv.latest_time:
            lv.latest_time = live_start_time
            global _subscribes
            _subscribes[str(roomId)]['latest_time'] = live_start_time
            # 跟新开播时间
            save_config(_subscribes, subs_path)
            sv.logger.info(f'检测到{lv.platform}{lv.room_id}直播间开播了')

            pic = f'[CQ:image,file={cover}]'.format(cover=cover)
            await notice(lv.room_id, f'开播提醒=========\n{pic}\n{title}\n{link}')
    else:
        # 未开播
        pass


async def check_other_live(lv):
    await lv.get()
    data = lv.parse_xml()
    if data.get('title'):  # 开播状态
        title = data['title']
        link = data['link']
        tuber = data['tuber']
        latest_time = data['latest_time']
        if latest_time != lv.latest_time:
            lv.latest_time = latest_time
            global _subscribes
            _subscribes[str(lv.room_id)]['latest_time'] = latest_time
            save_config(_subscribes, subs_path)
            sv.logger.info(f'检测到{lv.platform}{lv.room_id}直播间开播了')
            await notice(lv.room_id, f'开播提醒=========\n{tuber}\n{title}\n{link}')
    else:
        # 未开播
        pass


@sv.on_command('live', aliases='订阅直播推送', only_to_me=False)
async def subscribe(session: CommandSession):
    session.get('platform', prompt='请选择订阅的平台，目前支持哔哩哔哩和斗鱼')
    if session.state['platform'] == '哔哩哔哩' or session.state['platform'] == 'bilibili':
        platform = 'bilibili'
    elif session.state['platform'] == '斗鱼' or session.state['platform'] == 'douyu':
        platform = 'douyu'
    else:
        del session.state['platform']
        session.pause('参数错误，请重新输入')
    room = session.get('room', prompt='请输入订阅的房间号')
    if not session.state['room'].isdigit():
        del session.state['room']
        session.pause('参数错误，请重新输入')
    global _subscribes
    gid = session.event['group_id']
    if room in _subscribes.keys():
        if gid not in _subscribes[room]['subs_groups']:
            _subscribes[room]['subs_groups'].append(gid)
        else:
            await session.send('本群已经订阅过该直播间了')
            return
    else:
        _subscribes[room] = {
            "platform": platform,
            "room": int(room),
            "subs_groups": [gid],
            "latest_time": ""
        }
        lv = BiliLive(int(room))
        global _lives
        _lives.append(lv)
    if save_config(_subscribes, subs_path):
        await session.send('订阅成功')
    else:
        await session.send('订阅失败，请与bot维护中联系')


@sv.on_command('cancel_live', aliases=('取消直播推送', '取消直播提醒'))
async def cancel(session: CommandSession):
    room = session.get('room', prompt='请输入房间号')
    global _subscribes
    global _lives
    if room in _subscribes.keys():
        if len(_subscribes[room]['subs_groups']) == 1:  # 只有一个群订阅该直播
            for lv in _lives[::-1]:
                if lv.room_id == int(room):
                    _lives.remove(lv)
            del _subscribes[room]
            save_config(_subscribes, subs_path)
            sv.logger.info(f'成功取消直播间{room}的开播提醒')
            await session.send(f'成功取消直播间{room}直播提醒')
        else:
            gid = session.event['group_id']
            _subscribes[room]['subs_groups'].remove(gid)
            save_config(_subscribes, subs_path)
            await session.send(f'成功取消直播间{room}直播提醒')
