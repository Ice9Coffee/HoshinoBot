import re

from nonebot import on_command, CommandSession, MessageSegment
from aiocqhttp.exceptions import ActionFailed

from hoshino.log import logger
from hoshino.util import silence, concat_pic, pic2b64
from ..chara import Chara
from .arena import Arena

__plugin_name__ = 'arena'


@on_command('竞技场查询', aliases=('怎么拆', '怎么解', '怎么打', '如何拆', '如何解', '如何打', '怎麼拆', '怎麼解', '怎麼打'), only_to_me=False)
async def arena_query(session:CommandSession):

    argv = session.current_arg.strip()
    argv = re.sub(r'[?？呀啊哇]', ' ', argv)
    argv = argv.split()

    logger.info(f'竞技场查询：{argv}')

    if 0 >= len(argv):
        await session.finish('请输入防守方角色，用空格隔开')
    if 5 < len(argv):
        await session.finish('编队不能多于5名角色')


    defen = [ Chara.name2id(name) for name in argv ]
    for i, id_ in enumerate(defen):
        if Chara.UNKNOWN == id_:
            await session.finish(f'编队中含未知角色{argv[i]}，请尝试使用官方译名\n您也可以前往 github.com/Ice-Cirno/HoshinoBot/issues/5 回帖补充角色别称')
    if len(defen) != len(set(defen)):
        await session.finish('编队中出现重复角色')


    logger.debug('Arena doing query...')
    res = Arena.do_query(defen)
    logger.debug('Arena got response!')

    if res is None:
        await session.finish('查询出错，请联系维护组调教')

    if not len(res):
        await session.finish('抱歉没有查询到解法\n（注：没有作业不代表不能拆，竞技场没有无敌的守队只有不够深的box）')

    await silence(session, 30)       # 避免过快查询

    pics = [ Chara.gen_team_pic(entry['atk']) for entry in res[:min(6, len(res))] ]
    pics = concat_pic(pics)
    pics = pic2b64(pics)
    pics = MessageSegment.image(pics)

    header = f'已为{MessageSegment.at(session.ctx["user_id"])}骑士君查询到以下胜利队伍：\n'
    footer = '\n禁言是为了避免查询频繁，请打完本场竞技场后再来查询'
    msg = f'{header}{pics}{footer}'

    await session.send(msg)
