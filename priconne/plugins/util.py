import logging
from urllib.parse import urljoin, quote
from nonebot import on_command, CommandSession, MessageSegment
from aiocqhttp.exceptions import ActionFailed
from ._priconne_data import _PriconneData

USE_PRO_VERSION = True      # 是否使用酷Q PRO版功能，如撤回、发图等

IMG_BED = 'http://andong.ml/static/img/'    # 填写自己的图床地址





async def delete_msg(session:CommandSession, ban_time=0):
    group_id = session.ctx['group_id']
    user_id = session.ctx['user_id']
    msg_id = session.ctx['message_id']
    if ban_time:
        await session.bot.set_group_ban(group_id=group_id, user_id=user_id, duration=ban_time)
    try:
        if USE_PRO_VERSION:
            await session.bot.delete_msg(message_id=msg_id)
    except ActionFailed as e:
        print('retcode=', e.retcode, ' 撤回消息需要酷Q Pro版以及管理员权限')


def get_cqimg(filename, path='', img_bed=IMG_BED):
    print('img_bed=', img_bed)
    print('path=', path)
    print('filename=', filename)
    url = urljoin(img_bed, path) + '/'
    url = urljoin(url, quote(filename))
    print('cqimg url=', url)
    return str(MessageSegment.image(url))


class CharaHelper(object):

    NAME2ID = {}

    @staticmethod
    def __gen_name2id():
        CharaHelper.NAME2ID = {}
        for k,v in _PriconneData.CHARA.items():
            for s in v:
                if s not in CharaHelper.NAME2ID:
                    CharaHelper.NAME2ID[s] = k
                else:
                    logging.getLogger('priconne.plugins.util.CharaHelper.__gen_name2id()').error(
                        f'出现重名{s}于id{k}与id{CharaHelper.NAME2ID[s]}'
                    )
        pass


    @staticmethod
    def get_name(id_) -> str:
        return _PriconneData.CHARA[id_][0] if id_ in _PriconneData.CHARA else None


    @staticmethod
    def get_id(name) -> int:
        if not CharaHelper.NAME2ID:
            CharaHelper.__gen_name2id()
        return CharaHelper.NAME2ID[name] if name in CharaHelper.NAME2ID else -1


    @staticmethod
    def get_picname(id_) -> str:
        pic_pre = 'icon_unit_'
        pic_end = '31.png'
        return f'{pic_pre}{id_:0>4d}{pic_end}'


    @staticmethod
    def name2pic(name:str) -> str:
        id_ = CharaHelper.get_id(name)
        if not 1000 < id_ < 2000:
            id_ = 1000      # unknown character
        return CharaHelper.get_picname(id_)
