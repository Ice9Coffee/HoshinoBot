# 这是一份实例配置文件
# 将其修改为你需要的配置，并将文件名修改为config.py

from nonebot.default_config import *

DEBUG = False

SUPERUSERS = [10000]    # 填写超级用户的QQ号，可填多个用半角逗号","隔开
COMMAND_START = {''}    # 命令前缀（空字符串匹配任何消息）
COMMAND_SEP = set()     # 命令分隔符（hoshino不需要该特性，保持为set()即可）
NICKNAME = ''           # 机器人的昵称。呼叫昵称等同于@bot，可用元组配置多个昵称


# hoshino监听的端口与ip
PORT = 8080
HOST = '127.0.0.1'      # Windows部署使用此条配置
# HOST = '172.17.0.1'   # linux + docker使用此条配置
# docker桥的ip可能随环境不同而有变化
# 使用这行命令`ip addr show docker0 | grep -Po 'inet \K[\d.]+'`查看你的docker桥ip
# HOST = '172.18.0.1'   # 阿里云的linux + docker多数情况是这样
# HOST = '0.0.0.0'      # 开放公网访问使用此条配置（不安全）

IS_CQPRO = False        # 是否使用Pro版酷Q功能

# 资源库文件夹  Nonebot访问本机资源
RESOURCE_DIR = r'./res/'

# 资源库 URL  用于docker中的酷Q读取宿主机资源，注意以'/'结尾
# 若留空则图片均采用base64编码发送，开销较大但部署方便
# 若不清楚本项作用，请保持默认
RESOURCE_URL = ''

# 启用的模块
# 初次尝试部署时请先保持默认
# 如欲启用新模块，请认真阅读部署说明，逐个启用逐个配置
# 切忌一次性开启多个
MODULES_ON = {
    'botmanage',
    'dice',
    'groupmaster',
    # 'hourcall',
    # 'kancolle',
    # 'mikan',
    'pcrclanbattle',
    'priconne',
    # 'setu',
    # 'translate',
    # 'twitter',
}
