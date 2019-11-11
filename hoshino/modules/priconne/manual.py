from nonebot import on_command, CommandSession

@on_command('help', aliases=('man', 'manual', '帮助', '说明', '使用说明', '幫助', '說明', '使用說明'), only_to_me=False)
async def send_help(session:CommandSession):
    msg='''
目前支持的功能：[]替换为实际参数 注意使用空格分隔
- 会战管理：详见github.com/Ice-Cirno/HoshinoBot
- jjc查询：怎么拆 [角色1] [角色2] [...]
- 翻译：翻译 [文本]
- 查看rank推荐表：[前|中|后]卫rank表
- 查看卡池：卡池资讯

以下功能需at机器人：请手动at，复制无效
- 阅览官方四格：官漫[章节数] @bot
- 十连转蛋：来发十连 @bot
- 单抽转蛋：来发单抽 @bot
- 查看新番：来点新番 @bot
- 查阅jjc数据库网址：jjc作业网 @bot

主动推送：（如需开启/关闭请联系维护组）
- 时报
- 背刺时间提醒
- プリコネRe:Dive官方四格推送
- 番剧更新推送

以及其他隐藏功能:)
'''.strip()
    await session.send(msg)
