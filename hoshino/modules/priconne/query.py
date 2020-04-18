from hoshino import util
from hoshino.res import R
from hoshino.service import Service

sv = Service('pcr-query')

p1 = R.img('priconne/quick/r15-5-0.png').cqcode
p2 = R.img('priconne/quick/r15-5.png').cqcode
p4 = R.img('priconne/quick/r16-4-1.png').cqcode
p5 = R.img('priconne/quick/r16-4-2.png').cqcode
p6 = R.img('priconne/quick/r16-4-3.png').cqcode

@sv.on_rex(r'^(\*?([日台国b])服?([前中后]*)卫?)?rank(表|推荐|指南)?$', normalize=True, event='group')
async def rank_sheet(bot, ctx, match):
    is_jp = match.group(2) == '日'
    is_tw = match.group(2) == '台'
    is_cn = match.group(2) == '国' or match.group(2) == 'b'
    if not is_jp and not is_tw and not is_cn:
        await bot.send(ctx, '\n请问您要查询哪个服务器的rank表？\n*日rank表\n*台rank表\n*B服rank表\n※B服：开服仅开放至金装，r10前无需考虑卡rank，装备强化消耗较多mana，如非前排建议不强化', at_sender=True)
        return
    if is_jp:
        await util.silence(ctx, 60)
        await bot.send(ctx, '\n※不定期搬运，来源见图片\n※图中若有广告与本bot无关\n※升r有风险，强化需谨慎。表格仅供参考\n不要问我为什么不更新 我只是无情的搬运工 催更地址见图片\n※手机QQ更新后无法正常显示，故分条发送，如有刷屏还请谅解\nR16-4 rank表：', at_sender=True)
        await bot.send(ctx, str(p4))
        await bot.send(ctx, str(p5))
        await bot.send(ctx, str(p6))
    elif is_tw:
        await util.silence(ctx, 60)
        await bot.send(ctx, '\n※不定期搬运，来源见图片\n※图中若有广告与本bot无关\n※升r有风险，强化需谨慎。表格仅供参考\n本期争议较大 拿不准建议先卡着备足碎片\n※手机QQ更新后无法正常显示，故分条发送，如有刷屏还请谅解\nR15-5 rank表：', at_sender=True)
        await bot.send(ctx, str(p1))
        await bot.send(ctx, str(p2))
    elif is_cn:
        await bot.send(ctx, '\nB服：开服仅开放至金装，r10前无需考虑卡rank\n装备强化消耗较多mana，如非前排建议不强化\n唯一值得考量的是当前只开放至r9-3，保持r8满装满强或许会更强\n关于卡r的原因可发送"bcr速查"研读【为何卡R卡星】一帖', at_sender=True)


@sv.on_keyword(('pcr速查', 'pcr图书馆', 'pcr常用'))
async def query_sites(bot, ctx):
    msg='''
【日官网】priconne-redive.jp
【台官网】www.princessconnect.so-net.tw
【繁中wiki/兰德索尔图书馆】pcredivewiki.tw
【日文wiki/GameWith】gamewith.jp/pricone-re
【日文wiki/AppMedia】appmedia.jp/priconne-redive
【竞技场作业库(中文)】pcrdfans.com/battle
【竞技场作业库(日文)】nomae.net/arenadb
【论坛/NGA社区】bbs.nga.cn/thread.php?fid=-10308342
【iOS实用工具/初音笔记】bbs.nga.cn/read.php?tid=14878762
【安卓实用工具/静流笔记】bbs.nga.cn/read.php?tid=20499613

===其他查询输入以下关键词===
【日rank】【台rank】【jjc作业网】【黄骑充电表】【一个顶俩】
※B服速查请输入【bcr速查】'''
    await bot.send(ctx, msg, at_sender=True)
    await util.silence(ctx, 60)
    
    
@sv.on_keyword(('bcr速查', 'bcr攻略', 'bcr常用'))
async def query_sites_bilibili(bot, ctx):
    msg='''
【妈宝骑士攻略(懒人攻略合集)】bbs.nga.cn/read.php?tid=20980776
【机制详解】bbs.nga.cn/read.php?tid=19104807
【初始推荐】bbs.nga.cn/read.php?tid=20789582
【术语黑话】bbs.nga.cn/read.php?tid=18422680
【角色点评】bbs.nga.cn/read.php?tid=20804052
【秘石规划】bbs.nga.cn/read.php?tid=20101864
【卡池万里眼】bbs.nga.cn/read.php?tid=20816796
【为何卡R卡星】bbs.nga.cn/read.php?tid=20732035
【推图阵容推荐】bbs.nga.cn/read.php?tid=21010038

===其他查询输入以下关键词===
【日rank】【台rank】【jjc作业网】【黄骑充电表】【一个顶俩】
※日台服速查请输入【pcr速查】'''
    await bot.send(ctx, msg, at_sender=True)
    await util.silence(ctx, 60)

@sv.on_command('arena-database', aliases=('jjc', 'JJC', 'JJC作业', 'JJC作业网', 'JJC数据库', 'jjc作业', 'jjc作业网', 'pjjc作业网', 'jjc数据库', 'pjjc数据库', 'JJC作業', 'JJC作業網', 'JJC數據庫', 'jjc作業', 'jjc作業網', 'jjc數據庫'), only_to_me=False)
async def say_arina_database(session):
    await session.send('公主连接Re:Dive 竞技场编成数据库\n日文：https://nomae.net/arenadb \n中文：https://pcrdfans.com/battle')


@sv.on_keyword(('黄骑充电', '酒鬼充电', '黄骑充能', '酒鬼充能'), normalize=True, event='group')
async def yukari_sheet(bot, ctx):
    msg = f'''{R.img('priconne/quick/黄骑充电.jpg').cqcode}
※黄骑四号位例外较多
※图为PVP测试
※对面羊驼或中后卫坦时 有可能充歪
※我方羊驼算一号位'''
    await bot.send(ctx, msg, at_sender=True)


@sv.on_keyword(('一个顶俩', '拼音接龙'), normalize=True, event='group')
async def dragon(bot, ctx):
    msg = [ f"\n拼音对照表：{R.img('priconne/KyaruMiniGame/注音文字.jpg').cqcode}{R.img('priconne/KyaruMiniGame/接龙.jpg').cqcode}", 
           "龍的探索者們 小遊戲單字表 https://hanshino.nctu.me/online/KyaruMiniGame",
           "镜像 https://hoshino.monster/KyaruMiniGame", 
           "网站内有全词条和搜索，或需科学上网" ]
    await bot.send(ctx, '\n'.join(msg), at_sender=True)
