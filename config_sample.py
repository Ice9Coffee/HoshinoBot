# 这是一份实例配置文件
# 将其修改为你需要的配置，并将文件名修改为config.py

from nonebot.default_config import *

SUPERUSERS = {10000}   # 填写超级用户的QQ号
COMMAND_START = {'', '/', '!', '／', '！', '#'} # 命令开始符号（第一个是空字符串）
HOST = '172.17.0.1'    # 填写CQHTTP的ip，这里是docker的默认配置，如运行在本机，请改为127.0.0.1
PORT = 8080            # 填写CQHTTP的端口
