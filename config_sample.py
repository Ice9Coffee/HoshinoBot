# 这是一份实例配置文件
# 将其修改为你需要的配置，并将文件名修改为config.py

from nonebot.default_config import *

SUPERUSERS = [10000]    # 填写超级用户的QQ号
COMMAND_START = {''}    # 命令开始符号（第一个是空字符串）
HOST = '127.0.0.1'      # 填写CQHTTP的ip，docker的默认配置为172.17.0.1，WinServer部署则用127.0.0.1
PORT = 8080             # 填写CQHTTP的端口

# 是否使用Pro版酷Q功能
IS_CQPRO = False

# 资源库文件夹  Nonebot访问本机资源
RESOURCE_DIR = '~/.hoshino/res/'

# 资源库 URL  用于docker中的酷Q读取宿主机资源，注意以'/'结尾
# 若在WinServer上部署则不需本地WebServer，务必留空
RESOURCE_URL = ''
