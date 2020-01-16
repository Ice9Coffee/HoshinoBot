import os
import re
import sys
import logging
import ujson as json
from functools import wraps
from typing import Iterable, Optional, Callable, Union, NamedTuple, Set

import nonebot

from hoshino import util

"""
将一组功能包装为服务
支持的触发条件: on_message, on_keyword, on_rex, on_command, on_natural_language, scheduled_job

服务的配置文件格式为：
{
    "name": "ServiceName",
    "use_priv": Privilege.NORMAL,
    "manage_priv": Privilege.ADMIN,    
    "enable_on_default": true/false,
    "enable_group": [],
    "disable_group": []
}
默认储存位置：~/.hoshino/service_config/{ServiceName}.json
"""


class Privilege:
    BLACK = -999
    NORMAL = 0
    PRIVATE = 10
    PRIVATE_OTHER = 11
    PRIVATE_DISCUSS = 12
    PRIVATE_GROUP = 13
    PRIVATE_FRIEND = 14
    ADMIN = 21
    OWNER = 22
    WHITE = 51
    SUPERUSER = 999


_loaded_services = set()
_re_illegal_char = re.compile(r'[\\/:*?"<>|\.]')
_service_config_dir = os.path.expanduser('~/.hoshino/service_config/')
os.makedirs(_service_config_dir, exist_ok=True)


def _load_service_config(service_name):
    config_file = os.path.join(_service_config_dir, f'{service_name}.json')
    if not os.path.exists(config_file):
        # config file not found, return default config.
        return {
            "name": service_name,
            "use_priv": Privilege.NORMAL,
            "manage_priv": Privilege.ADMIN,
            "enable_on_default": True,
            "enable_group": [],
            "disable_group": []
        }
    with open(config_file) as f:
        config = json.load(f)
        return config


def _save_service_config(service):
    config_file = os.path.join(_service_config_dir, f'{service.name}.json')
    with open(config_file, 'w', encoding='utf8') as f:
        json.dump({
            "name": service.name,
            "use_priv": service.use_priv,
            "manage_priv": service.manage_priv,
            "enable_on_default": service.enable_on_default,
            "enable_group": service.enable_group,
            "disable_group": service.disable_group
        }, f, ensure_ascii=False)



class Service:
    __slots__ = (
        'name', 'use_priv', 'manage_priv', 'enable_on_default', 'enable_group', 'disable_group',
        'logger'
    )

    def __init__(self, name, use_priv=None, manage_priv=None, enable_on_default=None):

        assert not _re_illegal_char.search(name), 'Service name cannot contain character in [\\/:*?"<>|.]'
        config = _load_service_config(name)

        self.name = name
        self.use_priv = config['use_priv'] if use_priv == None else use_priv
        self.manage_priv = config['manage_priv'] if manage_priv == None else manage_priv
        self.enable_on_default = config['enable_on_default'] if enable_on_default == None else enable_on_default
        self.enable_group = set(config['enable_group'])
        self.disable_group = set(config['disable_group'])

        self.logger = logging.getLogger(name)
        default_handler = logging.StreamHandler(sys.stdout)
        default_handler.setFormatter(logging.Formatter(
            '[%(asctime)s %(name)s] %(levelname)s: %(message)s'
        ))
        self.logger.addHandler(default_handler)
        self.logger.setLevel(logging.DEBUG if nonebot.get_bot().config.DEBUG else logging.INFO)

        _loaded_services.add(self)


    @staticmethod
    def get_loaded_services() -> Set[Service]:
        return _loaded_services.copy()


    @staticmethod
    async def get_user_privilege(ctx):
        bot = nonebot.get_bot()
        if ctx['user_id'] in bot.config.SUPERUSERS:
            return Privilege.SUPERUSER
        # TODO: Black list & White list
        if ctx['message_type'] == 'private':
            if ctx['sub_type'] == 'friend':
                return Privilege.PRIVATE_FRIEND
            if ctx['sub_type'] == 'group':
                return Privilege.PRIVATE_GROUP
            if ctx['sub_type'] == 'discuss':
                return Privilege.PRIVATE_DISCUSS
            if ctx['sub_type'] == 'other':
                return Privilege.PRIVATE_OTHER
            return Privilege.PRIVATE
        if ctx['message_type'] == 'group':
            if not ctx['anomymous']:
                try:
                    member_info = await bot.get_group_member_info(group_id=ctx['group_id'], user_id=ctx['user_id'])
                    if member_info:
                        if member_info['role'] == 'owner':
                            return Privilege.OWNER
                        elif member_info['role'] == 'admin':
                            return Privilege.ADMIN
                        else:
                            return Privilege.NORMAL
                except nonebot.CQHttpError:
                    pass
        return Privilege.NORMAL


    async def check_permission(self, ctx, required_priv=None):
        required_priv = self.use_priv if required_priv == None else required_priv
        if ctx['message_type'] == 'group':
            group_id = ctx['group_id']
            if group_id in self.enable_group or (self.enable_on_default and group_id not in self.disable_group):
                user_priv = await self.get_user_privilege(ctx)
                return user_priv >= required_priv
            else:
                return False
        # TODO: 处理私聊权限。暂时不允许任何私聊
        return False


    async def get_group_list(self):
        """
        获取所有启用本服务的群
        """
        if self.enable_on_default:
            gl = await nonebot.get_bot().get_group_list()
            return set(gl) - self.disable_group
        else:
            return self.enable_group


    def set_enable(self, group_id):
        self.enable_group.add(group_id)
        self.disable_group.discard(group_id)
        _save_service_config(self)
    

    def set_disable(self, group_id):
        self.enable_group.discard(group_id)
        self.disable_group.add(group_id)
        _save_service_config(self)


    def on_message(self, arg=None):
        def deco(func):
            bot = nonebot.get_bot()
            @wraps
            async def wrapper(ctx):
                if await self.check_permission(ctx):
                    await func(ctx)
                    return
            return bot.on_message(arg)(wrapper)
        return deco


    def on_keyword(self, keywords:Iterable, arg=None):
        normalized_keywords = tuple(util.normalize_str(kw) for kw in keywords)
        def deco(func):
            @wraps
            async def wrapper(ctx):
                if await self.check_permission(ctx):
                    plain_text = util.normalize_str(ctx.extract_plain_text)
                    for kw in normalized_keywords:
                        if plain_text.find(kw) >= 0:
                            await func(ctx)
                            return
            return nonebot.get_bot().on_message()(wrapper)
        return deco


    def on_rex(self, rex):
        def deco(func):
            @wraps
            async def wrapper(ctx):
                if self.check_permission(ctx):
                    plain_text = util.normalize_str(ctx.extract_plain_text)
                    match = rex.search(plain_text)
                    if match:
                        await func(ctx, match)
                        return
            return nonebot.get_bot().on_message()(wrapper)            
        return deco


    def on_command(self, name, deny_tip=None, **kwargs):
        def deco(func):
            @wraps
            async def wrapper(session:nonebot.CommandSession):
                if await self.check_permission(session.ctx):
                    await func(session)
                elif deny_tip:
                    await session.send(deny_tip, at_sender=True)
                    return
            return nonebot.on_command(name, **kwargs)(wrapper)
        return deco


    def on_natural_language(self, keywords=None, **kwargs):
        def deco(func):
            @wraps
            async def wrapper(session):
                if await self.check_permission(session.ctx):
                    await func(session)
            return nonebot.on_natural_language(keywords, **kwargs)(wrapper)
        return deco


    def scheduled_job(self, *args, **kwargs):
        def deco(func):
            @wraps
            async def wrapper():
                await func(self.get_group_list())
            return nonebot.scheduler.scheduled_job(*args, **kwargs)(wrapper)
        return deco
