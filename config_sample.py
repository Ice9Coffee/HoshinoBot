# 这是一份实例配置文件
# 将其修改为你需要的配置，并将文件名修改为config.py

from nonebot.default_config import *

SUPERUSERS = [10000]    # 填写超级用户的QQ号，可填多个用半角逗号","隔开
COMMAND_START = {''}    # 命令前缀（空字符串匹配任何消息）
COMMAND_SEP = set()     # 命令分隔符（hoshino不需要该特性，保持为set()即可）

# hoshino监听的端口与ip
PORT = 8080
HOST = '127.0.0.1'      # Windows本地部署使用此条配置
# HOST = '172.17.0.1'   # docker使用此条配置
# HOST = '172.18.0.1'   # 阿里云服务器的docker使用此条配置

IS_CQPRO = False        # 是否使用Pro版酷Q功能

# 资源库文件夹  Nonebot访问本机资源
RESOURCE_DIR = '~/.hoshino/res/'

# 资源库 URL  用于docker中的酷Q读取宿主机资源，注意以'/'结尾
# 若留空则图片均采用base64编码发送，开销较大但部署方便
RESOURCE_URL = ''

# 启用的模块
# 初次尝试部署时请先保持默认
# 如欲启用新模块，请认真阅读部署说明，逐个配置逐个启用
MODULES_ON = {
    'botmanage',
    # 'deepchat',
    'dice',
    'groupmaster',
    # 'hourcall',
    # 'kancolle',
    # 'mikan',
    'pcrclanbattle',
    'priconne',
    # 'setu',
    'translate',
    # 'twitter',
}
