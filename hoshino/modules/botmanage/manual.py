from nonebot import on_command, CommandSession

@on_command('help', aliases=('manual', '帮助', '说明', '使用说明', '幫助', '說明', '使用說明'), only_to_me=False)
async def send_help(session:CommandSession):
    msg='''
【帮助】
下面是本bot支持的功能
输入冒号后的文本即可使用
注1：@bot 表明该功能必须at本bot才会触发
注2：请注意将参数用空格隔开
===从此开始↓一行距===

公主连接Re:Dive
- 抽卡模拟：@bot 来发十连 或 @bot 来发单抽
- jjc查询：怎么拆 布丁 饭团 兔子 小仓唯
- 查看bot卡池：看看卡池
- rank推荐表：日服rank 或 台服rank
- 常用网址：pcr速查
- プリコネRe:Dive官方四格查阅：官漫123
+ プリコネRe:Dive官方四格推送（默认开启）
- 会战管理（请见github.com/Ice-Cirno/HoshinoBot）

蜜柑番剧
* 启用本模块：开启 bangumi
- 查看最近更新：@bot 来点新番
+ 番剧推送（开启本模块后自动启用）

艦これ
+ 演习时间提醒：开启 kc-enshu-reminder
+ 时报：开启 hourcall

新型冠状病毒疫情播报
* 启用本模块：开启 nCoV2019
- 查看疫情总览：咳咳
- 查看疫情新闻：咳咳咳
+ 疫情新闻推送（开启本模块后自动启用）


通用
- 查看本群启用的功能：服务列表
- 启用功能：启用 service_name
- 禁用功能：禁用 service_name
- 机器翻译（限管理使用）： 翻译 もう一度、キミとつながる物語
- 联系作者：@bot 来杯咖啡

※调教时请注意使用频率，您的滥用可能会导致bot帐号被封禁
※本bot开源 可免费使用
※赞助支持请直接联系作者，您的支持是本bot更新维护的动力
'''.strip()
    await session.send(msg)
