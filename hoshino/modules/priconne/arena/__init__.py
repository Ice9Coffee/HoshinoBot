import re
import time
from collections import defaultdict

from nonebot import CommandSession, MessageSegment, get_bot
from hoshino.util import silence, concat_pic, pic2b64
from hoshino.service import Service, Privilege as Priv

sv = Service('pcr-arena', manage_priv=Priv.SUPERUSER)

from ..chara import Chara
from . import arena

DISABLE_NOTICE = '本群竞技场查询功能已禁用\n如欲开启，请与维护组联系'

_last_query_time = defaultdict(float)   # user_id: t in seconds
cd_time = 5                             # in seconds

@sv.on_command('竞技场查询', aliases=('jjc查询', '怎么拆', '怎么解', '怎么打', '如何拆', '如何解', '如何打', '怎麼拆', '怎麼解', '怎麼打'),
               deny_tip=DISABLE_NOTICE, only_to_me=False)
async def arena_query(session:CommandSession):

    arena.refresh_quick_key_dic()
    uid = session.ctx['user_id']
    now = time.time()    

    if now - cd_time < _last_query_time[uid]:
        await session.finish('您查询得过于频繁，请稍等片刻', at_sender=True)
    _last_query_time[uid] = now

    # 处理输入数据
    argv = session.current_arg_text.strip()
    argv = re.sub(r'[?？呀啊哇，,_]', ' ', argv)    
    argv = argv.split()
    sv.logger.debug(f'竞技场查询：{argv}')
    
    if 0 >= len(argv):
        await session.finish('请输入防守方角色，用空格隔开')
    if 5 < len(argv):
        await session.finish('编队不能多于5名角色')

    # 执行查询
    defen = [ Chara.name2id(name) for name in argv ]
    for i, id_ in enumerate(defen):
        if Chara.UNKNOWN == id_:
            await session.finish(f'编队中含未知角色{argv[i]}，请尝试使用官方译名\n您可@bot来杯咖啡+反馈未收录别称\n或前往 github.com/Ice-Cirno/HoshinoBot/issues/5 回帖补充')
    if len(defen) != len(set(defen)):
        await session.finish('编队中出现重复角色')
    if 1004 in defen:
        await session.send('⚠️您正在查询普通版炸弹人\n※万圣版可用万圣炸弹人/瓜炸等别称')

    sv.logger.info('Arena doing query...')
    res = await arena.do_query(defen, uid)
    sv.logger.info('Arena got response!')

    # 处理查询结果
    if res is None:
        await session.finish('查询出错，请联系维护组调教')
    if not len(res):
        await session.finish('抱歉没有查询到解法\n※没有作业说明随便拆 发挥你的想象力～★')
    res = res[:min(6, len(res))]    # 限制显示数量，截断结果

    # 发送回复
    if get_bot().config.IS_CQPRO:
        sv.logger.info('Arena generating picture...')
        atk_team_pic = [ Chara.gen_team_pic(entry['atk']) for entry in res ]
        atk_team_pic = concat_pic(atk_team_pic)
        atk_team_pic = pic2b64(atk_team_pic)
        atk_team_pic = str(MessageSegment.image(atk_team_pic))
        sv.logger.info('Arena picture ready!')
    else:
        atk_team_txt = '\n'.join(map(lambda entry: ' '.join(map(lambda x: f"{x.name}{x.star if x.star else ''}{'专' if x.equip else ''}" , entry['atk'])) , res))

    detail = [ "{qkey} 赞{up}+{my_up} 踩{down}+{my_down}".format_map(e) for e in res ]
    defen = [ Chara.fromid(x).name for x in defen ]
    defen = ' '.join(defen)
    defen = f'防守方【{defen}】'
    header = f'已为骑士君{MessageSegment.at(session.ctx["user_id"])}查询到以下进攻方案：'
    
    msg = [
        defen,
        header,
        atk_team_pic if get_bot().config.IS_CQPRO else atk_team_txt,
        '👍&👎：',
        *detail,
        '【NEW】发送"点赞/踩+作业id"即可进行评价，如"点赞 ABCDE"（不区分大小写，空格隔开）',
        'Support by pcrdfans_com'
    ]

    sv.logger.debug('Arena sending result...')
    await session.send('\n'.join(msg))
    sv.logger.debug('Arena result sent!')


@sv.on_command('点赞', only_to_me=False)
async def arena_like(session:CommandSession):
    qkey = session.current_arg_text.strip()
    uid = session.ctx['user_id']

    if not re.match(r'[0-9a-zA-Z]{5}', qkey):
        await session.finish('您要点赞的作业id不合法', at_sender=True)

    try:
        await arena.do_like(qkey, uid, action=1)
    except KeyError:
        await session.finish('无法找到作业id！您只能评价您最近查询过的作业', at_sender=True)
    
    await session.send('感谢您的反馈！', at_sender=True)


@sv.on_command('点踩', only_to_me=False)
async def arena_dislike(session:CommandSession):
    qkey = session.current_arg_text.strip()
    uid = session.ctx['user_id']

    if not re.match(r'[0-9a-zA-Z]{5}', qkey):
        await session.finish('您要点踩的作业id不合法', at_sender=True)

    try:
        await arena.do_like(qkey, uid, action=-1)
    except KeyError:
        await session.finish('无法找到作业id！您只能评价您最近查询过的作业', at_sender=True)
    
    await session.send('感谢您的反馈！', at_sender=True)
