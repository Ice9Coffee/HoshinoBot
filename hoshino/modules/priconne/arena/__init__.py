import re

from nonebot import CommandSession, MessageSegment, get_bot
from hoshino.util import silence, concat_pic, pic2b64
from hoshino.service import Service, Privilege as Priv
sv = Service('pcr-arena', manage_priv=Priv.SUPERUSER)

from ..chara import Chara
from .arena import Arena

DISABLE_NOTICE = '本群竞技场查询功能已禁用\n如欲开启，请与维护组联系'

@sv.on_command('竞技场查询', aliases=('jjc查询', '怎么拆', '怎么解', '怎么打', '如何拆', '如何解', '如何打', '怎麼拆', '怎麼解', '怎麼打'),
               deny_tip=DISABLE_NOTICE, only_to_me=False)
async def arena_query(session:CommandSession):

    # 处理输入数据
    argv = session.current_arg.strip()
    argv = re.sub(r'[?？呀啊哇]', ' ', argv)    
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
    res = await Arena.do_query(defen)
    sv.logger.info('Arena got response!')


    # 处理查询结果
    if res is None:
        await session.finish('查询出错，请联系维护组调教')

    if not len(res):
        await session.finish('抱歉没有查询到解法\n※没有作业说明随便拆 发挥你的想象力～★')

    await silence(session.ctx, 30)      # 避免过快查询

    res = res[:min(6, len(res))]    # 限制显示数量，截断结果

    # 发送回复
    if get_bot().config.IS_CQPRO:
        sv.logger.info('Arena generating picture...')
        atk_team_pic = [ Chara.gen_team_pic(entry['atk']) for entry in res ]
        atk_team_pic = concat_pic(atk_team_pic)
        atk_team_pic = pic2b64(atk_team_pic)
        atk_team_pic = MessageSegment.image(atk_team_pic)
        sv.logger.info('Arena picture ready!')
    else:
        atk_team_txt = '\n'.join(map(lambda entry: ' '.join(map(lambda x: f"{x.name}{x.star if x.star else ''}{'专' if x.equip else ''}" , entry['atk'])) , res))

    updown = [ f"赞{entry['up']} 踩{entry['down']}" for entry in res ]
    updown = '\n'.join(updown)
    defen = [ Chara.fromid(x).name for x in defen ]
    defen = ' '.join(defen)
    defen = f'【{defen}】'
    header = f'已为骑士君{MessageSegment.at(session.ctx["user_id"])}查询到以下进攻方案：'
    updown = f'👍&👎：\n{updown}'
    footer = '禁言是为避免频繁查询，请打完本场竞技场后再来查询'
    ref = 'Support by pcrdfans'
    
    if get_bot().config.IS_CQPRO:
        msg = f'{defen}\n{header}\n{atk_team_pic}\n{updown}\n{footer}\n{ref}'
    else:
        msg = f'{defen}\n{header}\n{atk_team_txt}\n{updown}\n{footer}\n{ref}'
        

    sv.logger.info('Arena sending result image...')
    await session.send(msg)
    # await session.send(atk_team_pic)
    sv.logger.info('Arena result image sent!')
