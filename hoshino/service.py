import os
import re
import sys
import pytz
import logging
import ujson as json
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict
from typing import Iterable, Optional, Callable, Union, NamedTuple, Set

import nonebot
from nonebot.command import _FinishException, _PauseException, SwitchException

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
    "visible": true/false,
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
_error_log_file = os.path.expanduser('~/.hoshino/error.log')
os.makedirs(_service_config_dir, exist_ok=True)

_black_list_group = {}


def _load_service_config(service_name):
    config_file = os.path.join(_service_config_dir, f'{service_name}.json')
    if not os.path.exists(config_file):
        # config file not found, return default config.
        return {
            "name": service_name,
            "use_priv": Privilege.NORMAL,
            "manage_priv": Privilege.ADMIN,
            "enable_on_default": True,
            "visible": True,
            "enable_group": [],
            "disable_group": []
        }
    with open(config_file, encoding='utf8') as f:
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
            "visible": service.visible,
            "enable_group": service.enable_group,
            "disable_group": service.disable_group
        }, f, ensure_ascii=False, indent=2)



class Service:

    def __init__(self, name, use_priv=None, manage_priv=None, enable_on_default=None, visible=None):
        """
        定义一个服务
        配置的优先级别：程序指定 > 配置文件 > 缺省值
        """
        assert not _re_illegal_char.search(name), 'Service name cannot contain character in [\\/:*?"<>|.]'
        config = _load_service_config(name)

        self.name = name
        self.use_priv = config.get('use_priv', Privilege.NORMAL) if use_priv is None else use_priv
        self.manage_priv = config.get('manage_priv', Privilege.ADMIN) if manage_priv is None else manage_priv
        self.enable_on_default = config.get('enable_on_default', True) if enable_on_default is None else enable_on_default
        self.visible = config.get('visible', True) if visible is None else visible
        self.enable_group = set(config['enable_group'])
        self.disable_group = set(config['disable_group'])

        formatter = logging.Formatter('[%(asctime)s %(name)s] %(levelname)s: %(message)s')
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG if self.bot.config.DEBUG else logging.INFO)
        default_handler = logging.StreamHandler(sys.stdout)
        default_handler.setFormatter(formatter)
        error_handler = logging.FileHandler(_error_log_file, encoding='utf8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(default_handler)
        self.logger.addHandler(error_handler)

        _loaded_services.add(self)


    @property
    def bot(self):
        return nonebot.get_bot()


    def get_self_ids(self):
        return self.bot._wsr_api_clients.keys()


    @staticmethod
    def get_loaded_services() -> Set["Service"]:
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
            if not ctx['anonymous']:
                try:
                    member_info = await bot.get_group_member_info(self_id=ctx['self_id'], group_id=ctx['group_id'], user_id=ctx['user_id'])
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
    
    
    @staticmethod
    def set_block_group(group_id, time):
        _black_list_group[group_id] = datetime.now() + time


    @staticmethod
    def check_block_group(group_id):
        if datetime.now() > _black_list_group[group_id]:
            del _black_list_group[group_id]
        return bool(group_id in _black_list_group)


    def check_enabled(self, group_id):
        return bool((group_id in self.enable_group) or (self.enable_on_default and group_id not in self.disable_group))


    async def check_permission(self, ctx, required_priv=None):
        required_priv = self.use_priv if required_priv == None else required_priv
        if ctx['message_type'] == 'group':
            group_id = ctx['group_id']
            if self.check_enabled(group_id) and not self.check_block_group(group_id):
                user_priv = await self.get_user_privilege(ctx)
                return bool(user_priv >= required_priv)
            else:
                return False
        # TODO: 处理私聊权限。暂时不允许任何私聊
        return False


    async def get_enable_groups(self) -> dict:
        """
        获取所有启用本服务的群
        { group_id: [self_id1, self_id2] }
        """
        gl = defaultdict(list)
        for sid in self.get_self_ids():
            sgl = set(g['group_id'] for g in await self.bot.get_group_list(self_id=sid))
            if self.enable_on_default:
                sgl = sgl - self.disable_group
            else:
                sgl = sgl & self.enable_group
            for g in sgl:
                gl[g].append(sid)
        return gl


    def set_enable(self, group_id):
        self.enable_group.add(group_id)
        self.disable_group.discard(group_id)
        _save_service_config(self)
        self.logger.info(f'Service {self.name} is enabled at group {group_id}')


    def set_disable(self, group_id):
        self.enable_group.discard(group_id)
        self.disable_group.add(group_id)
        _save_service_config(self)
        self.logger.info(f'Service {self.name} is disabled at group {group_id}')


    def on_message(self, event=None):
        def deco(func):
            @wraps(func)
            async def wrapper(ctx):
                if await self.check_permission(ctx):
                    try:
                        await func(self.bot, ctx)
                        self.logger.info(f'Message {ctx["message_id"]} is handled by {func.__name__}.')
                    except Exception as e:
                        self.logger.exception(e)
                        self.logger.error(f'{type(e)} occured when {func.__name__} handling message {ctx["message_id"]}.')
                    return
            return self.bot.on_message(event)(wrapper)
        return deco


    def on_keyword(self, keywords:Iterable, normalize=False, event=None):
        if isinstance(keywords, str):
            keywords = (keywords, )
        normalized_keywords = tuple(util.normalize_str(kw) for kw in keywords)
        def deco(func):
            @wraps(func)
            async def wrapper(ctx):
                if await self.check_permission(ctx):
                    plain_text = ctx['message'].extract_plain_text()
                    if normalize:
                        plain_text = util.normalize_str(plain_text)
                    ctx['plain_text'] = plain_text
                    for kw in normalized_keywords:
                        if plain_text.find(kw) >= 0:
                            try:
                                await func(self.bot, ctx)
                                self.logger.info(f'Message {ctx["message_id"]} is handled by {func.__name__}, triggered by keyword.')
                            except Exception as e:
                                self.logger.exception(e)
                                self.logger.error(f'{type(e)} occured when {func.__name__} handling message {ctx["message_id"]}.')
                            return
            return self.bot.on_message(event)(wrapper)
        return deco


    def on_rex(self, rex, normalize=False, event=None):
        if isinstance(rex, str):
            rex = re.compile(rex)            
        def deco(func):
            @wraps(func)
            async def wrapper(ctx):
                if await self.check_permission(ctx):
                    plain_text = ctx['message'].extract_plain_text()
                    if normalize:
                        plain_text = util.normalize_str(plain_text)
                    ctx['plain_text'] = plain_text                
                    match = rex.search(plain_text)
                    if match:
                        try:
                            await func(self.bot, ctx, match)
                            self.logger.info(f'Message {ctx["message_id"]} is handled by {func.__name__}, triggered by rex.')
                        except Exception as e:
                            self.logger.exception(e)
                            self.logger.error(f'{type(e)} occured when {func.__name__} handling message {ctx["message_id"]}.')
                        return
            return self.bot.on_message(event)(wrapper)
        return deco


    def on_command(self, name, *, deny_tip=None, **kwargs):
        def deco(func):
            @wraps(func)
            async def wrapper(session:nonebot.CommandSession):
                if await self.check_permission(session.ctx):
                    try:
                        await func(session)
                        self.logger.info(f'Message {session.ctx["message_id"]} is handled as command by {func.__name__}.')
                    except (_PauseException, _FinishException, SwitchException) as e:
                        raise e
                    except Exception as e:
                        self.logger.exception(e)
                        self.logger.error(f'{type(e)} occured when {func.__name__} handling message {session.ctx["message_id"]}.')
                    return
                elif deny_tip:
                    await session.send(deny_tip, at_sender=True)
                self.logger.info(f'Message {session.ctx["message_id"]} is a command of {func.__name__}. Permission denied.')
            return nonebot.on_command(name, **kwargs)(wrapper)
        return deco


    def on_natural_language(self, keywords=None, **kwargs):
        def deco(func):
            @wraps(func)
            async def wrapper(session:nonebot.NLPSession):
                if await self.check_permission(session.ctx):
                    try:
                        await func(session)
                        self.logger.info(f'Message {session.ctx["message_id"]} is handled as natural language by {func.__name__}.')
                    except Exception as e:
                        self.logger.exception(e)
                        self.logger.error(f'{type(e)} occured when {func.__name__} handling message {session.ctx["message_id"]}.')
                    return
            return nonebot.on_natural_language(keywords, **kwargs)(wrapper)
        return deco


    def scheduled_job(self, *args, **kwargs):
        kwargs.setdefault('timezone', pytz.timezone('Asia/Shanghai'))
        kwargs.setdefault('misfire_grace_time', 60)
        kwargs.setdefault('coalesce', True)
        def deco(func):
            async def wrapper():
                try:
                    self.logger.info(f'Scheduled job {func.__name__} start.')
                    gl = await self.get_enable_groups()
                    await func(gl)
                    self.logger.info(f'Scheduled job {func.__name__} completed.')
                except Exception as e:
                    self.logger.exception(e)
                    self.logger.error(f'{type(e)} occured when doing scheduled job {func.__name__}.')
            return nonebot.scheduler.scheduled_job(*args, **kwargs)(wrapper)
        return deco
