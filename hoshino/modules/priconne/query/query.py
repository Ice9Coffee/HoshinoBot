import itertools
from datetime import datetime
from hoshino import util, R
from hoshino.typing import CQEvent
from . import sv

rank_tw = '21-3'
rank_cn = '14-5'
pcn = R.img(f'priconne/quick/r{rank_cn}-cn-0.png').cqcode
ptw = (
    R.img(f'priconne/quick/r{rank_tw}-tw-0.png').cqcode +
    R.img(f'priconne/quick/r{rank_tw}-tw-1.png').cqcode +
    R.img(f'priconne/quick/r{rank_tw}-tw-2.png').cqcode +
    R.img(f'priconne/quick/r{rank_tw}-tw-3.png').cqcode
)


def get_jp_support_rank(t: datetime):
    delta = t - datetime(2021, 8, 15)
    years, days = divmod(delta.days, 365)
    rank = 21 + (years * 12 + days // 30) // 3
    return rank


@sv.on_rex(r'^(\*?([日台国陆b])服?([前中后]*)卫?)?rank(表|推荐|指南)?$')
async def rank_sheet(bot, ev):
    match = ev['match']
    is_jp = match.group(2) == '日'
    is_tw = match.group(2) == '台'
    is_cn = match.group(2) and match.group(2) in '国陆b'
    if not is_jp and not is_tw and not is_cn:
        await bot.send(ev, '\n请问您要查询哪个服务器的rank表？\n*日rank表\n*台rank表\n*陆rank表', at_sender=True)
        return
    msg = [
        '\n※rank表仅供参考，升r有风险，强化需谨慎\n※请以会长要求为准',
    ]
    if is_jp:
        await bot.send(ev, f"\n休闲：输出拉满 辅助R{get_jp_support_rank(datetime.now())}-0\n一档：问你家会长", at_sender=True)
    elif is_tw:
        msg.append(f'※不定期搬运自漪夢奈特\nR{rank_tw}参考表：\n{ptw}\n※详见油管频道https://www.youtube.com/playlist?list=PLYMR7DEWZIdsG1DSXe6HuNZT0M4jIozK2\n')
        await bot.send(ev, '\n'.join(msg), at_sender=True)
        await util.silence(ev, 60)
    elif is_cn:
        msg.append(f'※不定期搬运自nga\n※制作by樱花铁道之夜\nR{rank_cn} rank表：\n{pcn}')
        await bot.send(ev, '\n'.join(msg), at_sender=True)
        await util.silence(ev, 60)


@sv.on_fullmatch('jjc', 'JJC', 'JJC作业', 'JJC作业网', 'JJC数据库', 'jjc作业', 'jjc作业网', 'jjc数据库')
async def say_arina_database(bot, ev):
    await bot.send(ev, '公主连接Re:Dive 竞技场编成数据库\n日文：https://nomae.net/arenadb \n中文：https://pcrdfans.com/battle')


OTHER_KEYWORDS = '【日rank】【台rank】【b服rank】【jjc作业网】【黄骑充电表】【一个顶俩】'
PCR_SITES = f'''
【繁中wiki/兰德索尔图书馆】pcredivewiki.tw
【日文wiki/GameWith】gamewith.jp/pricone-re
【日文wiki/AppMedia】appmedia.jp/priconne-redive
【竞技场作业库(中文)】pcrdfans.com/battle
【竞技场作业库(日文)】nomae.net/arenadb
【论坛/NGA社区】bbs.nga.cn/thread.php?fid=-10308342
【iOS实用工具/初音笔记】bbs.nga.cn/read.php?tid=14878762
【安卓实用工具/静流笔记】bbs.nga.cn/read.php?tid=20499613
【台服卡池千里眼】bbs.nga.cn/read.php?tid=28236922
【日官网】priconne-redive.jp
【台官网】www.princessconnect.so-net.tw

===其他查询关键词===
{OTHER_KEYWORDS}
※B服速查请输入【bcr速查】'''

BCR_SITES = f'''
【妈宝骑士攻略(懒人攻略合集)】bbs.nga.cn/read.php?tid=20980776
【机制详解】bbs.nga.cn/read.php?tid=19104807
【初始推荐】bbs.nga.cn/read.php?tid=20789582
【术语黑话】bbs.nga.cn/read.php?tid=18422680
【角色点评】bbs.nga.cn/read.php?tid=20804052
【秘石规划】bbs.nga.cn/read.php?tid=20101864
【卡池亿里眼】bbs.nga.cn/read.php?tid=20816796
【为何卡R卡星】bbs.nga.cn/read.php?tid=20732035
【推图阵容推荐】bbs.nga.cn/read.php?tid=21010038

===其他查询关键词===
{OTHER_KEYWORDS}
※日台服速查请输入【pcr速查】'''

@sv.on_fullmatch('pcr速查', 'pcr图书馆', '图书馆')
async def pcr_sites(bot, ev: CQEvent):
    await bot.send(ev, PCR_SITES, at_sender=True)
    await util.silence(ev, 60)
@sv.on_fullmatch('bcr速查', 'bcr攻略')
async def bcr_sites(bot, ev: CQEvent):
    await bot.send(ev, BCR_SITES, at_sender=True)
    await util.silence(ev, 60)


YUKARI_SHEET_ALIAS = map(lambda x: ''.join(x), itertools.product(('黄骑', '酒鬼'), ('充电', '充电表', '充能', '充能表')))
YUKARI_SHEET = f'''
{R.img('priconne/quick/黄骑充电.jpg').cqcode}
※大圈是1动充电对象 PvP测试
※黄骑四号位例外较多
※对面羊驼或中后卫坦 有可能歪
※我方羊驼算一号位
※图片搬运自漪夢奈特'''
@sv.on_fullmatch(YUKARI_SHEET_ALIAS)
async def yukari_sheet(bot, ev):
    await bot.send(ev, YUKARI_SHEET, at_sender=True)
    await util.silence(ev, 60)


DRAGON_TOOL = f'''
拼音对照表：{R.img('priconne/KyaruMiniGame/注音文字.jpg').cqcode}{R.img('priconne/KyaruMiniGame/接龙.jpg').cqcode}
龍的探索者們小遊戲單字表 https://hanshino.nctu.me/online/KyaruMiniGame
镜像 https://hoshino.monster/KyaruMiniGame
网站内有全词条和搜索，或需科学上网'''
@sv.on_fullmatch('一个顶俩', '拼音接龙', '韵母接龙')
async def dragon(bot, ev):
    await bot.send(ev, DRAGON_TOOL, at_sender=True)
    await util.silence(ev, 60)


@sv.on_fullmatch('千里眼')
async def future_gacha(bot, ev):
    await bot.send(ev, "亿里眼·一之章 bbs.nga.cn/read.php?tid=21317816\n亿里眼·二之章 bbs.nga.cn/read.php?tid=25358671")
    await util.silence(ev, 60)
