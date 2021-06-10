from aiocqhttp.message import MessageSegment
from hoshino.service import Service, priv
from hoshino.typing import HoshinoBot, CQEvent as Event
from .._interact import interact, ActSession
from hoshino.util import silence
from random import randint, shuffle
from itertools import cycle

sv_help = """
"""

sv = Service(
    name='俄罗斯轮盘赌',
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 是否可见
    enable_on_default=True,  # 是否默认启用
    bundle='娱乐',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(('轮盘赌', '俄罗斯轮盘赌'))
async def roulette(bot: HoshinoBot, ev: Event):
    try:
        session = ActSession.from_event('俄罗斯轮盘赌', ev, max_user=3, usernum_limit=True)
        interact.add_session(session)
        await bot.send(ev, '游戏开始,目前有1位玩家，还缺1名玩家，发送"参与轮盘赌"加入游戏')
    except ValueError as e:
        await bot.finish(ev, f'{e}')


@sv.on_fullmatch('参与轮盘赌')
async def join_roulette(bot: HoshinoBot, ev: Event):
    session = interact.find_session(ev, name='俄罗斯轮盘赌')
    if not session:  # session未创建
        await bot.send(ev, '游戏未创建，发送轮盘赌或者俄罗斯轮盘赌创建游戏')
        return  # 不处理
    try:
        interact.join_session(ev, session)
        await bot.send(ev, f'成功加入,目前有{session.count_user()}位玩家,发送“开始”进行游戏')

    except ValueError as e:
        await bot.finish(ev, f'{e}')


@interact.add_action('俄罗斯轮盘赌', (f'{MessageSegment.face(169)}', '开枪'))
async def fire(event: Event, session: ActSession):
    if not session.state.get('started'):
        await session.finish(event, '请先发送“开始”进行游戏')

    if not session.pos:
        session.state['pos'] = randint(1, 6)  # 拨动轮盘，pos为第几发是子弹 """
    if not session.state.get('times'):
        session.state['times'] = 1

    if event.user_id != session.state.get('turn'):
        await session.finish(event, '现在枪不在你手上哦~')

    pos = session.pos
    times = session.times
    if pos == times:  # shoot
        session.close()
        await session.send(event, '枪响了，你死了！')
        await silence(event, 60)
    elif times == 5:
        session.close()
        user = session.rotate.__next__()
        await session.send(event, f'你长舒了一口气，并反手击毙了{MessageSegment.at(user)}')
        await session.bot.set_group_ban(group_id=event.group_id, user_id=user, duration=60)
    else:
        session.state['times'] += 1
        session.state['turn'] = session.rotate.__next__()
        await session.send(event, f'无事发生,轮到{MessageSegment.at(session.state["turn"])}开枪')


@interact.add_action('俄罗斯轮盘赌', '开始')
async def start_roulette(event: Event, session: ActSession):
    if session.count_user() < 2:
        await session.finish(event, '人数不足')

    if not session.state.get('started'):
        session.state['started'] = True
        rule = """
        轮盘容量为6，但只填充了一发子弹，请参与游戏的双方轮流发送开枪，枪响结束
        """.strip()
        if not session.rotate:  # user轮流
            shuffle(session.users)
            session.state['rotate'] = cycle(session.users)
        if not session.turn:
            session.state['turn'] = session.rotate.__next__()
        await session.send(event, f'游戏开始,{rule}现在请{MessageSegment.at(session.state["turn"])}开枪')
    else:
        await session.send(event, '游戏已经开始了')
