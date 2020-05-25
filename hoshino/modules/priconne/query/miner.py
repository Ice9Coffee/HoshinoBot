import numpy as np
from . import sv

this_season = np.zeros(15001)
all_season = np.zeros(15001)

this_season[1:11] = 50
this_season[11:101] = 10
this_season[101:201] = 5
this_season[201:501] = 3
this_season[501:1001] = 2
this_season[1001:2001] = 2
this_season[2001:4000] = 1
this_season[4000:8000:100] = 50
this_season[8100:15001:100] = 15

all_season[1:11] = 500
all_season[11:101] = 50
all_season[101:201] = 30
all_season[201:501] = 10
all_season[501:1001] = 5
all_season[1001:2001] = 3
all_season[2001:4001] = 2
all_season[4001:7999] = 1
all_season[8100:15001:100] = 30

@sv.on_command('arena_miner', aliases=('挖矿', 'jjc钻石', '竞技场钻石', 'jjc钻石查询', '竞技场钻石查询'))
async def arena_miner(session):
    try:
        rank = int(session.current_arg_text)
        rank = np.clip(rank, 1, 15001)
    except:
        session.finish(f'请输入"挖矿 纯数字最高排名"', at_sender=True)
    s_all = int(all_season[1:rank].sum())
    s_this = int(this_season[1:rank].sum())
    msg = f"\n最高排名奖励还剩 {s_this} 钻\n历届最高排名还剩 {s_all} 钻"
    await session.send(msg, at_sender=True)
