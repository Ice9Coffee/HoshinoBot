import asyncio
import hashlib
import json
import os
import random
import re
from os import path
from typing import List, Union

import aiohttp
import filetype
import nonebot
from aiocqhttp.event import Event
from aiocqhttp.exceptions import ActionFailed
from nonebot import scheduler

from hoshino.log import new_logger
from hoshino.service import Service

logger = new_logger('shebot', debug=False)
bot = nonebot.get_bot()


async def download_async(url: str, save_path: str, save_name: str, auto_extension=False) -> str:
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            content = await resp.read()
            if auto_extension:  # 没有指定后缀，自动识别后缀名
                try:
                    extension = filetype.guess_mime(content).split('/')[1]
                except:
                    raise ValueError('不是有效文件类型')
                abs_path = path.join(save_path, f'{save_name}.{extension}')
            else:
                abs_path = path.join(save_path, save_name)
            with open(abs_path, 'wb') as f:
                f.write(content)
                return abs_path


def get_random_file(path) -> str:
    files = os.listdir(path)
    rfile = random.choice(files)
    return rfile


def get_md5(val: Union[bytes, str]) -> str:
    if isinstance(val, str):
        val = val.encode('utf-8')
    m = hashlib.md5()
    m.update(val)
    return m.hexdigest()


async def broadcast(msg, groups=None, sv_name=None):
    bot = nonebot.get_bot()
    # 当groups指定时，在groups中广播；当groups未指定，但sv_name指定，将在开启该服务的群广播
    svs = Service.get_loaded_services()
    if not groups and sv_name not in svs:
        raise ValueError(f'不存在服务 {sv_name}')
    if sv_name:
        enable_groups = await svs[sv_name].get_enable_groups()
        send_groups = enable_groups.keys() if not groups else groups
    else:
        send_groups = groups
    for gid in send_groups:
        try:
            await bot.send_group_msg(group_id=gid, message=msg)
            logger.info(f'群{gid}投递消息成功')
            await asyncio.sleep(0.5)
        except ActionFailed as e:
            logger.error(f'在群{gid}投递消息失败,  retcode={e.retcode}')
        except Exception as e:
            logger.exception(e)


def extract_url_from_event(event: Event) -> List[str]:
    urls = re.findall(r'http.*?term=\d', str(event.message))
    return urls


def save_config(config: dict, path: str):
    try:
        with open(path, 'w', encoding='utf8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as ex:
        logger.error(ex)
        return False


def load_config(path):
    try:
        with open(path, mode='r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    except Exception as ex:
        logger.error(f'exception occured when loading config in {path}  {ex}')
        logger.exception(ex)
        return {}


class RSS():
    def __init__(self):
        self.base_url = 'http://101.32.36.8:1200'
        self.route: str = None
        self.xml: bytes = None
        self.filter: dict = dict()
        self.filterout: dict = dict()  # out为过滤掉
        '''
        filter 选出想要的内容
        filter: 过滤标题和描述
        filter_title: 过滤标题
        filter_description: 过滤描述
        filter_author: 过滤作者
        filter_time: 过滤时间，仅支持数字，单位为秒。返回指定时间范围内的内容。如果条目没有输出pubDate或者格式不正确将不会被过滤
        '''
        self.filter_case_sensitive = True  # 过滤是否区分大小写,默认区分大小写
        self.limit = 10  # 限制最大条数，主要用于排行榜类 RSS

    async def get(self):
        url = self.base_url + self.route
        params = {}
        for key in self.filter:
            if self.filter[key]:
                params[key] = self.filter[key]
        for key in self.filterout:
            if self.filterout[key]:
                params[key] = self.filterout[key]
        params['limit'] = self.limit
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                self.xml = await resp.read()

    def parse_xml(self):
        # 在实现类中编写解析xml函数
        raise NotImplementedError
