import re
import os
import json
import logging
from nonebot import on_command, CommandSession, MessageSegment
from nonebot.permission import GROUP_MEMBER, GROUP_ADMIN
from aiocqhttp.exceptions import ActionFailed
from .gacha import Gacha
from .arena import Arena
from ..util import delete_msg, silence, get_cqimg, CharaHelper, USE_PRO_VERSION


gacha_10_aliases = ('十连', '十连！', '十连抽', '来个十连', '来发十连', '来次十连', '抽个十连', '抽发十连', '抽次十连', '十连扭蛋', '扭蛋十连',
                    '10连', '10连！', '10连抽', '来个10连', '来发10连', '来次10连', '抽个10连', '抽发10连', '抽次10连', '10连扭蛋', '扭蛋10连',
                    '十連', '十連！', '十連抽', '來個十連', '來發十連', '來次十連', '抽個十連', '抽發十連', '抽次十連', '十連轉蛋', '轉蛋十連',
                    '10連', '10連！', '10連抽', '來個10連', '來發10連', '來次10連', '抽個10連', '抽發10連', '抽次10連', '10連轉蛋', '轉蛋10連')
gacha_1_aliases = ('单抽', '单抽！', '来发单抽', '来个单抽', '来次单抽', '扭蛋单抽', '单抽扭蛋',
                   '單抽', '單抽！', '來發單抽', '來個單抽', '來次單抽', '轉蛋單抽', '單抽轉蛋')


def get_config():
    config_file = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_file) as f:
        config = json.load(f)
        return config

def check_gacha_permission(group_id):
    config = get_config()
    return not (group_id in config["GACHA_DISABLE_GROUP"])


@on_command('gacha_1', aliases=gacha_1_aliases, only_to_me=True)
async def gacha_1(session:CommandSession):

    if not check_gacha_permission(session.ctx['group_id']):
        await session.finish('本群转蛋功能已禁用')
        return

    at = str(MessageSegment.at(session.ctx['user_id']))
    
    gacha = Gacha()
    res, star, hiishi = gacha.gacha_one(gacha.up_prob, gacha.s3_prob, gacha.s2_prob)
    silence_time = hiishi * 60

    if USE_PRO_VERSION:
        # 转成CQimg
        res = get_cqimg(CharaHelper.get_picname(CharaHelper.get_id(res)), 'priconne/unit') + f'{res} {"★"*star}'


    # await delete_msg(session)
    await silence(session, silence_time)
    msg = f'{at}\n素敵な仲間が増えますよ！\n{res}'
    # print(msg)
    print('len(msg)=', len(msg))
    await session.send(msg)


@on_command('gacha_10', aliases=gacha_10_aliases, only_to_me=True)
async def gacha_10(session:CommandSession):

    if not check_gacha_permission(session.ctx['group_id']):
        await session.finish('本群转蛋功能已禁用')
        return

    at = str(MessageSegment.at(session.ctx['user_id']))
    
    gacha = Gacha()
    result, hiishi = gacha.gacha_10()
    silence_time = hiishi * 6 if hiishi < 200 else hiishi * 60

    if USE_PRO_VERSION:
        # 转成CQimg
        result = [ (CharaHelper.get_id(x), star, 0) for x, star in result ]
        res1 = CharaHelper.gen_team_pic(result[ :5], star_slot_verbose=False)
        res2 = CharaHelper.gen_team_pic(result[5: ], star_slot_verbose=False)
        res = CharaHelper.concat_team_pic([res1, res2])
        res = CharaHelper.pic2b64(res)
        res = MessageSegment.image(res)
    else:
        result = [ f'{x}{"★"*star}' for x, star in result]
        res1 = ' '.join(result[0:5])
        res2 = ' '.join(result[5: ])
        res = f'{res1}\n{res2}'

    # await delete_msg(session)
    await silence(session, silence_time)
    msg = f'{at}\n素敵な仲間が増えますよ！\n{res}'
    # print(msg)
    print('len(msg)=', len(msg))
    await session.send(msg)


@on_command('卡池资讯', aliases=('看看卡池', '康康卡池'), only_to_me=False)
async def gacha_info(session:CommandSession):
    gacha = Gacha()
    up_chara = gacha.up
    if USE_PRO_VERSION:
        up_chara = map(lambda x: get_cqimg(CharaHelper.get_picname(CharaHelper.get_id(x)), 'priconne/unit') + x, up_chara)
    up_chara = '\n'.join(up_chara)
    await session.send(f"本期卡池主打的角色：\n{up_chara}\nUP角色合计={(gacha.up_prob/10):.1f}% 3星出率={(gacha.s3_prob)/10:.1f}%")
    # await delete_msg(session)


@on_command('竞技场查询', aliases=('怎么拆', '怎么解', '怎么打', '如何拆', '如何解', '如何打'), only_to_me=False)
async def arena_query(session:CommandSession):

    logger = logging.getLogger('kokkoro.arena_query')
    logger.setLevel(logging.DEBUG)

    argv = session.current_arg.strip()
    print(argv)
    argv = re.sub(r'[\?？呀啊哇]', ' ', argv)
    print(argv)
    argv = argv.split()
    print(argv)

    print(f'竞技场查询：{argv}')
    logger.info(f'竞技场查询：{argv}')

    if 0 >= len(argv):
        await session.send('请输入防守方角色，用空格隔开')
        return
    if 5 < len(argv):
        await session.send('编队不能多于5名角色')
        return
    defen = Arena.user_input(argv)
    if 100001 in defen:
        await session.send('编队中含未知角色，请尝试使用官方译名')
        return 
    if len(defen) != len(set(defen)):
        await session.send('编队中出现重复角色')
        return

    res = Arena.do_query(defen)

    if not len(res):
        await session.send('抱歉没有查询到解法\n（注：没有作业不代表不能拆，竞技场没有无敌的守队只有不够深的box）')
        return

    await silence(session, 120)       # 避免过快查询

    print('query completed, Start generating pics')
    pics = [ CharaHelper.gen_team_pic(team, 128) for team in res ]
    print('pic generated. Start concat pics')
    pics = CharaHelper.concat_team_pic(pics)
    print('concat finished. Converting to base64')
    pics = CharaHelper.pic2b64(pics)
    print('base64 ready! len=', len(pics))
    pics = MessageSegment.image(pics)

    header = f'已为{MessageSegment.at(session.ctx["user_id"])}骑士君查询到以下胜利队伍：\n'
    footer = '\n禁言是为了避免查询频繁，请打完本场竞技场后再来查询'
    msg = f'{header}{pics}{footer}'
    print('len(msg)=', len(msg))

    logger.info('sending pics...')
    await session.send(msg)
    logger.info('Finished sending.')
