from nonebot import on_command, CommandSession, MessageSegment
from nonebot.permission import GROUP_MEMBER, GROUP_ADMIN
from aiocqhttp.exceptions import ActionFailed
from .gacha import Gacha
from ..util import delete_msg, get_cqimg, CharaHelper, USE_PRO_VERSION


@on_command('十连', aliases=('十连抽', '来个十连', '来发十连', '十连扭蛋'), only_to_me=False)
async def gacha_10(session:CommandSession):
    at = str(MessageSegment.at(session.ctx['user_id']))
    
    result, hiishi = Gacha.gacha_10(fes=False)
    silence_time = hiishi * 6 if hiishi < 60 else hiishi * 60

    if USE_PRO_VERSION:
        # 转成CQimg
        result = [ get_cqimg(CharaHelper.get_picname(CharaHelper.get_id(x)), 'priconne') for x in result ]
        res1 = ''.join(result[0:5])
        res2 = ''.join(result[5: ])
    else:
        res1 = ' '.join(result[0:5])
        res2 = ' '.join(result[5: ])

    await delete_msg(session, silence_time)
    await session.send(
        f'{at}\n新たな仲間が増えますよ！\n{res1}\n{res2}'
    )


@on_command('卡池资讯', aliases=('看看卡池', '康康卡池'), only_to_me=True)
async def gacha_info(session:CommandSession):
    up_chara = Gacha.up
    if USE_PRO_VERSION:
        up_chara = map(lambda x: get_cqimg(CharaHelper.get_picname(CharaHelper.get_id(x)), 'priconne') + x, up_chara)
    up_chara = '\n'.join(up_chara)
    await session.send(f"本期卡池主打的角色：\n{up_chara}\nUP角色合计=0.7% 3星出率=2.5%")
    await delete_msg(session)


    
