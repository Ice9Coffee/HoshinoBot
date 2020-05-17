import itertools
from hoshino import util, R, CommandSession
from . import sv

p1 = R.img('priconne/quick/r16-3-tw-0.png').cqcode
p2 = R.img('priconne/quick/r16-3-tw-1.png').cqcode
p4 = R.img('priconne/quick/r17-3-jp-1.png').cqcode
p5 = R.img('priconne/quick/r17-3-jp-2.png').cqcode
p6 = R.img('priconne/quick/r17-3-jp-3.png').cqcode
p7 = R.img('priconne/quick/r8-3.jpg').cqcode

@sv.on_rex(r'^(\*?([日台国b])服?([前中后]*)卫?)?rank(表|推荐|指南)?$', normalize=True)
async def rank_sheet(bot, ctx, match):
    is_jp = match.group(2) == '日'
    is_tw = match.group(2) == '台'
    is_cn = match.group(2) == '国' or match.group(2) == 'b'
    if not is_jp and not is_tw and not is_cn:
        await bot.send(ctx, '\n请问您要查询哪个服务器的rank表？\n*日rank表\n*台rank表\n*B服rank表\n※B服：当前仅开放至金装，r10前无需考虑卡rank，装备强化消耗较多mana，如非前排建议不强化', at_sender=True)
        return
    msg = [
        '\n※表格仅供参考，升r有风险，强化需谨慎',
    ]
    if is_jp:
        msg.append('※不定期搬运自图中群号\n※图中广告为原作者推广，与本bot无关\nR17-3 rank表：')
        pos = match.group(3)
        if not pos or '前' in pos:
            msg.append(str(p4))
        if not pos or '中' in pos:
            msg.append(str(p5))
        if not pos or '后' in pos:
            msg.append(str(p6))
        await bot.send(ctx, '\n'.join(msg), at_sender=True)
        await util.silence(ctx, 60)
    elif is_tw:
        msg.append(f'※不定期搬运自漪夢奈特\n※油管有介绍视频及原文档\nR16-3 rank表：\n{p1}{p2}')
        await bot.send(ctx, '\n'.join(msg), at_sender=True)
        await util.silence(ctx, 60)
    elif is_cn:
        await bot.send(ctx, '\n※B服当前仅开放至金装，r10前无需考虑卡rank\n※暂未发现公开的靠谱rank推荐表\n※装备强化消耗较多mana，如非前排建议不强化\n※关于卡r的原因可发送"bcr速查"研读【为何卡R卡星】一帖', at_sender=True)
        # await bot.send(ctx, str(p7))
        # await util.silence(ctx, 60)


@sv.on_command('arena-database', aliases=('jjc', 'JJC', 'JJC作业', 'JJC作业网', 'JJC数据库', 'jjc作业', 'jjc作业网', 'jjc数据库', 'JJC作業', 'JJC作業網', 'JJC數據庫', 'jjc作業', 'jjc作業網', 'jjc數據庫'), only_to_me=False)
async def say_arina_database(session):
    await session.send('公主连接Re:Dive 竞技场编成数据库\n日文：https://nomae.net/arenadb \n中文：https://pcrdfans.com/battle')


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
【台服卡池千里眼】bbs.nga.cn/read.php?tid=16986067
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

@sv.on_command('pcr-sites', aliases=('pcr速查', 'pcr图书馆', 'pcr圖書館', '图书馆', '圖書館'))
async def pcr_sites(session:CommandSession):
    await session.send(PCR_SITES, at_sender=True)
    await util.silence(session.ctx, 60)
@sv.on_command('bcr-sites', aliases=('bcr速查', 'bcr攻略'))
async def bcr_sites(session:CommandSession):
    await session.send(BCR_SITES, at_sender=True)
    await util.silence(session.ctx, 60)


YUKARI_SHEET_ALIAS = map(lambda x: ''.join(x), itertools.product(('黄骑', '酒鬼', '黃騎'), ('充电', '充电表', '充能', '充能表')))
YUKARI_SHEET = f'''
{R.img('priconne/quick/黄骑充电.jpg').cqcode}
※大圈是1动充电对象 PvP测试
※黄骑四号位例外较多
※对面羊驼或中后卫坦 有可能歪
※我方羊驼算一号位
※图片搬运自漪夢奈特'''
@sv.on_command('yukari-sheet', aliases=YUKARI_SHEET_ALIAS)
async def yukari_sheet(session:CommandSession):
    await session.send(YUKARI_SHEET, at_sender=True)
    await util.silence(session.ctx, 60)


DRAGON_TOOL = f'''
拼音对照表：{R.img('priconne/KyaruMiniGame/注音文字.jpg').cqcode}{R.img('priconne/KyaruMiniGame/接龙.jpg').cqcode}
龍的探索者們小遊戲單字表 https://hanshino.nctu.me/online/KyaruMiniGame
镜像 https://hoshino.monster/KyaruMiniGame
网站内有全词条和搜索，或需科学上网'''
@sv.on_command('拼音接龙', aliases=('一个顶俩', '韵母接龙'))
async def dragon(session:CommandSession):
    await session.send(DRAGON_TOOL, at_sender=True)
    await util.silence(session.ctx, 60)
