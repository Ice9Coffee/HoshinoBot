import re
import time
from collections import defaultdict

from nonebot import CommandSession, MessageSegment, get_bot
from hoshino.util import silence, concat_pic, pic2b64, FreqLimiter
from hoshino.service import Service, Privilege as Priv

sv = Service('pcr-arena', manage_priv=Priv.SUPERUSER)

from ..chara import Chara
from . import arena

DISABLE_NOTICE = '本群竞技场查询功能已禁用\n如欲开启，请与维护组联系'

lmt = FreqLimiter(5)

aliases = ('怎么拆', '怎么解', '怎么打', '如何拆', '如何解', '如何打', '怎麼拆', '怎麼解', '怎麼打', 'jjc查询', 'jjc查詢')
aliases_b = tuple('b' + a for a in aliases) + tuple('B' + a for a in aliases)
aliases_tw = tuple('台' + a for a in aliases)
aliases_jp = tuple('日' + a for a in aliases)

@sv.on_command('竞技场查询', aliases=aliases, deny_tip=DISABLE_NOTICE, only_to_me=False)
async def arena_query(session:CommandSession):
    await _arena_query(session, region=1)

@sv.on_command('b竞技场查询', aliases=aliases_b, deny_tip=DISABLE_NOTICE, only_to_me=False)
async def arena_query_b(session:CommandSession):
    await _arena_query(session, region=2)

@sv.on_command('台竞技场查询', aliases=aliases_tw, deny_tip=DISABLE_NOTICE, only_to_me=False)
async def arena_query_tw(session:CommandSession):
    await _arena_query(session, region=3)

@sv.on_command('日竞技场查询', aliases=aliases_jp, deny_tip=DISABLE_NOTICE, only_to_me=False)
async def arena_query_jp(session:CommandSession):
    await _arena_query(session, region=4)


async def _arena_query(session:CommandSession, region:int):

    arena.refresh_quick_key_dic()
    uid = session.ctx['user_id']

    if not lmt.check(uid):
        session.finish('您查询得过于频繁，请稍等片刻', at_sender=True)
    lmt.start_cd(uid)

    # 处理输入数据
    argv = session.current_arg_text.strip()
    argv = re.sub(r'[?？，,_]', ' ', argv)
    argv = argv.split()
    if 0 >= len(argv):
        session.finish('请输入防守方角色，用空格隔开', at_sender=True)
    if 5 < len(argv):
        session.finish('编队不能多于5名角色', at_sender=True)

    defen = [ Chara.name2id(name) for name in argv ]
    for i, id_ in enumerate(defen):
        if Chara.UNKNOWN == id_:
            await session.finish(f'编队中含未知角色"{argv[i]}"，请尝试使用官方译名\n您可@bot来杯咖啡+反馈未收录别称\n或前往 github.com/Ice-Cirno/HoshinoBot/issues/5 回帖补充', at_sender=True)
    if len(defen) != len(set(defen)):
        await session.finish('编队中出现重复角色', at_sender=True)
    if 1004 in defen:
        await session.send('\n⚠️您正在查询普通版炸弹人\n※万圣版可用万圣炸弹人/瓜炸等别称', at_sender=True)

    # 执行查询
    sv.logger.info('Doing query...')
    res = await arena.do_query(defen, uid, region)
    sv.logger.info('Got response!')

    # 处理查询结果
    if res is None:
        session.finish('查询出错，请联系维护组调教\n请先移步pcrdfans.com进行查询', at_sender=True)
    if not len(res):
        session.finish('抱歉没有查询到解法\n※没有作业说明随便拆 发挥你的想象力～★\n作业上传请前往pcrdfans.com', at_sender=True)
    res = res[:min(6, len(res))]    # 限制显示数量，截断结果

    # 发送回复
    if get_bot().config.IS_CQPRO:
        sv.logger.info('Arena generating picture...')
        atk_team = [ Chara.gen_team_pic(entry['atk']) for entry in res ]
        atk_team = concat_pic(atk_team)
        atk_team = pic2b64(atk_team)
        atk_team = str(MessageSegment.image(atk_team))
        sv.logger.info('Arena picture ready!')
    else:
        atk_team = '\n'.join(map(lambda entry: ' '.join(map(lambda x: f"{x.name}{x.star if x.star else ''}{'专' if x.equip else ''}" , entry['atk'])) , res))

    details = [ " ".join([
        f"赞{e['up']}+{e['my_up']}" if e['my_up'] else f"赞{e['up']}",
        f"踩{e['down']}+{e['my_down']}" if e['my_down'] else f"踩{e['down']}",
        e['qkey']
    ]) for e in res ]

    defen = [ Chara.fromid(x).name for x in defen ]
    defen = f"防守方【{' '.join(defen)}】"
    at = str(MessageSegment.at(session.ctx["user_id"]))

    msg1 = [
        defen,
        f'已为骑士{at}查询到以下进攻方案：',
        f'{atk_team}Support by pcrdfans_com'
    ]
    msg2 = [
        f'为骑士{at}查询到作业评价👍&👎：', 
        *details,
        '※发送"点赞/点踩"可进行评价',
        '※手机QQ无法正常显示图片故分条发送 如有刷屏还请谅解',
    ]
    if region == 1:
        msg2.append('※使用"b怎么拆"或"台怎么拆"可按服过滤')

    sv.logger.debug('Arena sending result...')
    await session.send('\n'.join(msg1))
    await session.send('\n'.join(msg2))
    sv.logger.debug('Arena result sent!')


@sv.on_command('点赞', only_to_me=False)
async def arena_like(session:CommandSession):
    await _arena_feedback(session, 1)

@sv.on_command('点踩', only_to_me=False)
async def arena_dislike(session:CommandSession):
    await _arena_feedback(session, -1)

rex_qkey = re.compile(r'^[0-9a-zA-Z]{5}$')
async def _arena_feedback(session:CommandSession, action:int):
    action_tip = '赞' if action > 0 else '踩'
    qkey = session.current_arg_text.strip()
    if not qkey:
        session.finish(f'请发送"点{action_tip}+作业id"，如"点{action_tip} ABCDE"，空格隔开不分大小写', at_sender=True)
    if not rex_qkey.match(qkey):
        session.finish(f'您要点{action_tip}的作业id不合法', at_sender=True)
    try:
        uid = session.ctx['user_id']
        await arena.do_like(qkey, uid, action)
    except KeyError:
        session.finish('无法找到作业id！您只能评价您最近查询过的作业', at_sender=True)
    await session.send('感谢您的反馈！', at_sender=True)
