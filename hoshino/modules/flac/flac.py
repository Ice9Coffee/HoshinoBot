"""无损音乐搜索 数据来自acgjc.com"""
from hoshino import Service, priv, logger, aiorequests
from hoshino.typing import CQEvent
from urllib.parse import quote

sv = Service('flac', help_='[搜无损] +关键词搜索')

@sv.on_prefix('搜无损')
async def search_flac(bot, ev: CQEvent):
    keyword = ev.message.extract_plain_text()
    resp = await aiorequests.get('http://mtage.top:8099/acg-music/search', params={'title-keyword': keyword}, timeout=1)
    res = await resp.json()
    if res['success'] is False:
        logger.error(f"Flac query failed.\nerrorCode={res['errorCode']}\nerrorMsg={res['errorMsg']}")
        await bot.finish(ev, f'查询失败 请至acgjc官网查询 www.acgjc.com/?s={quote(keyword)}', at_sender=True)

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
        '数据来自 www.acgjc.com',
        f'更多结果可见 www.acgjc.com/?s={quote(keyword)}'
    ]

    await bot.send(ev, '\n'.join(msg), at_sender=True)
