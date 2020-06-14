"""
无损音乐搜索 数据来自acgjc.com
"""
import requests

from hoshino import Service, Privilege, CommandSession, logger
from urllib.parse import quote

sv = Service('flac', manage_priv=Privilege.SUPERUSER, enable_on_default=True, visible=True)


@sv.on_command('搜无损')
async def search_flac(session: CommandSession):
    keyword = session.current_arg_text
    resp = requests.get('http://mtage.top:8099/acg-music/search', params={'title-keyword': keyword}, timeout=1)
    res = resp.json()
    if res['success'] is False:
        logger.error(f"Flac query failed.\nerrorCode={res['errorCode']}\nerrorMsg={res['errorMsg']}")
        session.finish(f'查询失败 请至acgjc官网查询 http://www.acgjc.com/?s={quote(keyword)}', at_sender=True)

    music_list = res['result']['content']
    music_list = music_list[:min(5, len(music_list))]

    details = [" ".join([
        f"{ele['title']}",
        f"{ele['downloadLink']}",
        f"密码：{ele['downloadPass']}" if ele['downloadPass'] else ""
    ]) for ele in music_list]

    msg = [
        f"共 {res['result']['totalElements']} 条结果" if len(music_list) > 0 else '没有任何结果',
        *details,
        '数据来自 http://www.acgjc.com',
        f'当前库内不包括acgjc的全部数据，更多结果可见 http://www.acgjc.com/?s={quote(keyword)}'
    ]

    session.finish('\n'.join(msg), at_sender=True)
