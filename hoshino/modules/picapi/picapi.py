# -- coding: UTF-8 --
import os
import re
import time
import datetime
import random
import urllib
import urllib.request
import requests
import io
import hoshino
from lxml import etree
from nonebot import on_command
from hoshino import R, Service, priv, util


class RandomC:
    @staticmethod
    def get_R_path():
        return hoshino.config.picapi._PIC_PATH

    @staticmethod
    def get_R_url():
        return hoshino.config.picapi._PIC_URL

    @staticmethod
    def get_R_key():
        return hoshino.config.picapi._PIC_keyword

    @staticmethod
    def get_R_DIR():
        return hoshino.config.__bot__.RES_DIR


sv_help = """
随机图片
""".strip()

sv = Service(
    name='随机图片',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=False,  # 是否可见
    enable_on_default=False,  # 是否默认启用
    bundle='随机图片',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_message('group')
async def randomACG_pic(bot, ctx):
    file_path = RandomC.get_R_path()
    acgrandow_key = RandomC.get_R_key()
    rd_url = RandomC.get_R_url()
    for i in range(len(acgrandow_key)):
        msg = str(ctx.message)
        if msg != acgrandow_key[i]:
            continue
        else:
            url_t = rd_url[i].split('|')
            url = random.choice(url_t)
            print('调用url:', url)
            try:
                headers = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36 Edg/81.0.416.50'
                }
                nowtime = int(time.time())
                resp = requests.get(url, headers)
                if resp.status_code != 200:
                    await bot.send(ctx, '额~刚找到的图片，它丢惹', at_sender=False)
                    return
                resp_size = resp.content
                size = io.BytesIO(resp_size).read()
                if len(size) >= 200:
                    filename = '{}0.jpg'.format(nowtime)
                    # print('filename:',filename)
                    file_address = '{}/{}'.format(file_path, filename)
                    # 直接下载
                    with open(file_address, 'wb') as f:
                        f.write(resp.content)
                        f.close()
                    pppic = RandomC.get_R_DIR() + 'img/'
                    ppic = file_path.replace(pppic, '')
                    pic = ppic + '/' + filename
                    # 得到次级文件位置
                    print('file_address:', file_address)
                    await bot.send(ctx, R.img(pic).cqcode, at_sender=False)
                    return
                resp.encoding = 'UTF-8'
                html = etree.HTML(resp.text)
                image_url = html.xpath('//img/@src')[0]
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                    # 如果没有这个path则直接创建
                # file_suffix = os.path.splitext(image_url)
                filename = '{}0.jpg'.format(nowtime)
                file_address = '{}/{}'.format(file_path, filename)
                # 拼接文件名。
                print('file_address:', file_address)
                urllib.request.urlretrieve(image_url, file_address)
                # 下载
                pppic = RandomC.get_R_DIR() + 'img/'
                ppic = file_path.replace(pppic, '')
                pic = ppic + '/' + filename
                await bot.send(ctx, R.img(pic).cqcode, at_sender=False)
                return
            except IOError as e:
                print('1Error:', e)
            except Exception as e:
                print('2Error:', e)
