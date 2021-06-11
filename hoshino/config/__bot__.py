"""这是一份实例配置文件

将其修改为你需要的配置，并将文件夹config_example重命名为config
"""

# hoshino监听的端口与ip
PORT = 8080
HOST = '127.0.0.1'  # 本地部署使用此条配置（QQ客户端和bot端运行在同一台计算机）
# HOST = '0.0.0.0'      # 开放公网访问使用此条配置（不安全）

DEBUG = False  # 调试模式

SUPERUSERS = [794329728]  # 填写超级用户的QQ号，可填多个用半角逗号","隔开
NICKNAME = r'菜狗|at,qq=2289875995'  # 机器人的昵称。呼叫昵称等同于@bot，可用元组配置多个昵称

COMMAND_START = {''}  # 命令前缀（空字符串匹配任何消息）
COMMAND_SEP = set()  # 命令分隔符（hoshino不需要该特性，保持为set()即可）

# 发送图片的协议
# 可选 http, file, base64
# 当QQ客户端与bot端不在同一台计算机时，可用http协议
RES_PROTOCOL = 'file'
# 资源库文件夹，需可读可写，windows下注意反斜杠转义
RES_DIR = r'./res/'
# 使用http协议时需填写，原则上该url应指向RES_DIR目录
RES_URL = 'http://127.0.0.1:5000/static/'

'''------- CQHTTP -------'''
IMAGE_PATH = "~/go/src/cqhttp/data/images"  # cqhttp用这条,保持默认即可

'''---------shebot 网址----------'''
IP = 'bot.jianxiaodai.com'  # 修改为你的服务器ip,推荐修改
public_address = 'bot.jianxiaodai.com'  # 修改为你的服务器ip+端口,推荐修改
PassWord = '31894267'  # 登录一些只限维护人知道密码的网页

'''-------------apikeys---------------'''
''' 
lolicon_api,相关插件setu_mix,申请地址https://api.lolicon.app/#/setu?id=apikey
'''
lolicon_api = ''
'''
acggov_api ,相关插件setu_mix,
申请地址https://www.acgmx.com/
'''
ACG_GOV_API = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJQb3NzaWJsZSIsInV1aWQiOiI5Njk5OTg1ZTBhODk0NWI4OTkwODFiOWZhNzQ2YzgyYiIsImlhdCI6MTYyMzI4OTgzMywiYWNjb3VudCI6IntcImVtYWlsXCI6XCI3OTQzMjk3MjhAcXEuY29tXCIsXCJnZW5kZXJcIjotMSxcImhhc1Byb25cIjowLFwiaWRcIjo5NTIsXCJwYXNzV29yZFwiOlwiMWM2YmVkZGNlYzg1MmM2MGI4NDM2NDg1NmEwOTFkMDFcIixcInN0YXR1c1wiOjAsXCJ1c2VyTmFtZVwiOlwiUG9zc2libGVcIn0iLCJqdGkiOiI5NTIifQ.ZL8N_yK6NOiVS2JO7jOB_kZTicflpPuVPaHbcyuN9eE'

'''tenxun_api,相关插件aichat,申请地址https://ai.qq.com/,已经为你默认准备了一个,但建议自行申请进行个性定制
'''
# app_id = '2151738429'
# app_key = 'YktgDw71PBeqPaEC'
tenxun_api_ID = '2154581933'  # 仅供测试用的默认apikey，画像：名字：冰川镜华 年龄：8岁
tenxun_api_KEY = 'gtv1yCMqKSKSoeuD'  # 建议更换

'''----  腾讯云 ----'''
AppId = '1252268453'  # 腾讯云
SecretId = 'AKIDTlnY2GDtIPGq89tMYT8WcRzGGzRdYDdn'
SecretKey = 'vZx6yYrsd7KGwLTJtDF0UifLktlNjpeC'

'''---- 百度云 ----'''
baidu_api_ID = ''
baidu_api_KEY = ''
baidu_api_SECRET = ''

# 启用的模块
# 初次尝试部署时请先保持默认
# 如欲启用新模块，请认真阅读部署说明，逐个启用逐个配置
# 切忌一次性开启多个
MODULES_ON = {
    'aichat',  # 需要apikey，用前修改概率
    'aircon',  # 群空调
    'anticoncurrency',  # 反并发插件
    'bilidynamicpush',  # B站动态
    # 'bilisearchspider',  # b站订阅
    'botchat',  # 机器人chat
    'botmanage',  # 机器人管理
    # 'deepchat', # 复读
    # 'explosion',  # 惠惠
    # 'generate_image',  # 取代原image
    'generator',  # 营销文生成等五个小功能
    'groupmanager',  # 群管插件
    'groupmaster',  # 群聊基础功能
    'historyToday',  # 历史上的今天
    'lxsay',  # 鲁迅说
    'meme_web',  # meme_generator的web化,勿同时开启
    'nbnhhsh',  # 将抽象短语转化为好好说话
    'nmsl',  # 抽象抽象抽抽抽像像像
    'picapi',  # 自定义拉取图片
    # 'portune',  # 运势插件
    'reload',  # 重启
    # 'revgif',  # GIF图倒放
    # 'russian',  # 俄罗斯轮盘赌
    # 'setu_mix',  # 俩涩图插件合二为一
    'shaojo',  # 今天也是美少女
    'shebot',  # 插件合集，来源https://github.com/pcrbot/plugins-for-Hoshino,其中的接头需要百度云api
    'vortune',  # 抽签
    'weather',  # 天气插件
    'what_to_eat',  # 今天吃啥
}
