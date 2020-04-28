import os
import re
import sys
import pytz
import random
import logging
import asyncio
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict
from typing import Iterable, Optional, Callable, Union, NamedTuple, Set, Dict, Any
try:
    import ujson as json
except:
    import json

import nonebot
from nonebot import NoneBot, CommandSession
from nonebot.command import _FinishException, _PauseException, SwitchException

from hoshino import util, logger




class Privilege:
    """The privilege of user discribed in an `int` number.

    `0` is for Default or NotSet. The other numbers may change in future versions.
    """
    BLACK = -999
    DEFAULT = 0
    NORMAL = 1
    PRIVATE = 10
    PRIVATE_OTHER = 11
    PRIVATE_DISCUSS = 12
    PRIVATE_GROUP = 13
    PRIVATE_FRIEND = 14
    ADMIN = 21
    OWNER = 22
    WHITE = 51
    SUPERUSER = 999

# service management
_loaded_services:Dict[str, "Service"] = {}   # {name: service}
_re_illegal_char = re.compile(r'[\\/:*?"<>|\.]')
_service_config_dir = os.path.expanduser('~/.hoshino/service_config/')
os.makedirs(_service_config_dir, exist_ok=True)

# logging
_error_log_file = os.path.expanduser('~/.hoshino/error.log')
_critical_log_file = os.path.expanduser('~/.hoshino/critical.log')
_formatter = logging.Formatter('[%(asctime)s %(name)s] %(levelname)s: %(message)s')
_default_handler = logging.StreamHandler(sys.stdout)
_default_handler.setFormatter(_formatter)
_error_handler = logging.FileHandler(_error_log_file, encoding='utf8')
_error_handler.setLevel(logging.ERROR)
_error_handler.setFormatter(_formatter)
_critical_handler = logging.FileHandler(_critical_log_file, encoding='utf8')
_critical_handler.setLevel(logging.CRITICAL)
_critical_handler.setFormatter(_formatter)

# block list
_black_list_group = {}  # Dict[group_id, expr_time]
_black_list_user = {}   # Dict[user_id, expr_time]


def _load_service_config(service_name):
    config_file = os.path.join(_service_config_dir, f'{service_name}.json')
    if not os.path.exists(config_file):
        return {}   # config file not found, return default config.
    try:
        with open(config_file, encoding='utf8') as f:
            config = json.load(f)
            return config
    except Exception as e:
        logger.exception(e)
        return {}


def _save_service_config(service):
    config_file = os.path.join(_service_config_dir, f'{service.name}.json')
    with open(config_file, 'w', encoding='utf8') as f:
        json.dump({
            "name": service.name,
            "use_priv": service.use_priv,
            "manage_priv": service.manage_priv,
            "enable_on_default": service.enable_on_default,
            "visible": service.visible,
            "enable_group": list(service.enable_group),
            "disable_group": list(service.disable_group)
        }, f, ensure_ascii=False, indent=2)



class Service:
    """将一组功能包装为服务, 提供增强的触发条件与分群权限管理.

    支持的触发条件:
    `on_message`, `on_keyword`, `on_rex`, `on_command`, `on_natural_language`

    提供接口：
    `scheduled_job`, `broadcast`

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

    储存位置：
    `~/.hoshino/service_config/{ServiceName}.json`
    """

    def __init__(self, name, use_priv=None, manage_priv=None, enable_on_default=None, visible=None):
        """
        定义一个服务
        配置的优先级别：配置文件 > 程序指定 > 缺省值
        """
        assert not _re_illegal_char.search(name), 'Service name cannot contain character in [\\/:*?"<>|.]'

        config = _load_service_config(name)
        self.name = name
        self.use_priv = config.get('use_priv') or use_priv or Privilege.NORMAL
        self.manage_priv = config.get('manage_priv') or manage_priv or Privilege.ADMIN
        self.enable_on_default = config.get('enable_on_default')
        if self.enable_on_default is None:
            self.enable_on_default = enable_on_default
        if self.enable_on_default is None:
            self.enable_on_default = True
        self.visible = config.get('visible')
        if self.visible is None:
            self.visible = visible
        if self.visible is None:
            self.visible = True
        self.enable_group = set(config.get('enable_group', []))
        self.disable_group = set(config.get('disable_group', []))

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG if self.bot.config.DEBUG else logging.INFO)
        self.logger.addHandler(_default_handler)
        self.logger.addHandler(_error_handler)
        self.logger.addHandler(_critical_handler)

        assert self.name not in _loaded_services, f'Service name "{self.name}" already exist!'
        _loaded_services[self.name] = self


    @property
    def bot(self):
        return nonebot.get_bot()

    @staticmethod
    def get_self_ids():
        return nonebot.get_bot()._wsr_api_clients.keys()

    @staticmethod
    def get_loaded_services() -> Dict[str, "Service"]:
        return _loaded_services

    @staticmethod
    def set_block_group(group_id, time):
        _black_list_group[group_id] = datetime.now() + time

    @staticmethod
    def set_block_user(user_id, time):
        if user_id not in nonebot.get_bot().config.SUPERUSERS:
            _black_list_user[user_id] = datetime.now() + time

    @staticmethod
    def check_block_group(group_id):
        if group_id in _black_list_group and datetime.now() > _black_list_group[group_id]:
            del _black_list_group[group_id]     # 拉黑时间过期
            return False
        return bool(group_id in _black_list_group)

    @staticmethod
    def check_block_user(user_id):
        if user_id in _black_list_user and datetime.now() > _black_list_user[user_id]:
            del _black_list_user[user_id]       # 拉黑时间过期
            return False
        return bool(user_id in _black_list_user)

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

    def check_enabled(self, group_id):
        return bool((group_id in self.enable_group) or (self.enable_on_default and group_id not in self.disable_group))

    @staticmethod
    def get_user_priv(ctx):
        bot = nonebot.get_bot()
        uid = ctx['user_id']
        if uid in bot.config.SUPERUSERS:
            return Privilege.SUPERUSER
        if Service.check_block_user(uid):
            return Privilege.BLACK
        # TODO: White list
        if ctx['message_type'] == 'group':
            if not ctx['anonymous']:
                role = ctx['sender'].get('role')
                if role == 'member':
                    return Privilege.NORMAL
                elif role == 'admin':
                    return Privilege.ADMIN
                elif role == 'owner':
                    return Privilege.OWNER
            return Privilege.NORMAL
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
        return Privilege.NORMAL

    def check_priv(self, ctx, required_priv=None):
        required_priv = self.use_priv if required_priv is None else required_priv
        if ctx['message_type'] == 'group':
            return bool(self.get_user_priv(ctx) >= required_priv)
        else:
            # TODO: 处理私聊权限。暂时不允许任何私聊
            return False

    def _check_all(self, ctx):
        gid = ctx.get('group_id', 0)
        return self.check_enabled(gid) and not self.check_block_group(gid) and self.check_priv(ctx)

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


    def on_message(self, event='group') -> Callable:
        def deco(func:Callable[[NoneBot, Dict], Any]) -> Callable:
            @wraps(func)
            async def wrapper(ctx):
                if self._check_all(ctx):
                    try:
                        await func(self.bot, ctx)
                        # self.logger.info(f'Message {ctx["message_id"]} is handled by {func.__name__}.')
                    except Exception as e:
                        self.logger.exception(e)
                        self.logger.error(f'{type(e)} occured when {func.__name__} handling message {ctx["message_id"]}.')
                    return
            return self.bot.on_message(event)(wrapper)
        return deco


    def on_keyword(self, keywords:Iterable, *, normalize=True, event='group') -> Callable:
        if isinstance(keywords, str):
            keywords = (keywords, )
        if normalize:
            keywords = tuple(util.normalize_str(kw) for kw in keywords)
        def deco(func:Callable[[NoneBot, Dict], Any]) -> Callable:
            @wraps(func)
            async def wrapper(ctx):
                if self._check_all(ctx):
                    plain_text = ctx['message'].extract_plain_text()
                    if normalize:
                        plain_text = util.normalize_str(plain_text)
                    ctx['plain_text'] = plain_text
                    for kw in keywords:
                        if kw in plain_text:
                            try:
                                await func(self.bot, ctx)
                                self.logger.info(f'Message {ctx["message_id"]} is handled by {func.__name__}, triggered by keyword.')
                            except Exception as e:
                                self.logger.exception(e)
                                self.logger.error(f'{type(e)} occured when {func.__name__} handling message {ctx["message_id"]}.')
                            return
            return self.bot.on_message(event)(wrapper)
        return deco


    def on_rex(self, rex, normalize=True, event='group') -> Callable:
        if isinstance(rex, str):
            rex = re.compile(rex)
        def deco(func:Callable[[NoneBot, Dict, re.Match], Any]) -> Callable:
            @wraps(func)
            async def wrapper(ctx):
                if self._check_all(ctx):
                    plain_text = ctx['message'].extract_plain_text()
                    plain_text = plain_text.strip()
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


    def on_command(self, name, *, only_to_me=False, deny_tip=None, **kwargs) -> Callable:
        kwargs['only_to_me'] = only_to_me
        def deco(func:Callable[[CommandSession], Any]) -> Callable:
            @wraps(func)
            async def wrapper(session:CommandSession):
                if session.ctx['message_type'] != 'group':
                    return
                if not self.check_enabled(session.ctx['group_id']):
                    self.logger.debug(f'Message {session.ctx["message_id"]} is command of a disabled service, ignored.')
                    if deny_tip:
                        session.finish(deny_tip, at_sender=True)
                    return
                if self._check_all(session.ctx):
                    try:
                        await func(session)
                        self.logger.info(f'Message {session.ctx["message_id"]} is handled as command by {func.__name__}.')
                    except (_PauseException, _FinishException, SwitchException) as e:
                        raise e
                    except Exception as e:
                        self.logger.exception(e)
                        self.logger.error(f'{type(e)} occured when {func.__name__} handling message {session.ctx["message_id"]}.')
                    return
            return nonebot.on_command(name, **kwargs)(wrapper)
        return deco


    def on_natural_language(self, keywords=None, **kwargs) -> Callable:
        def deco(func) -> Callable:
            @wraps(func)
            async def wrapper(session:nonebot.NLPSession):
                if self._check_all(session.ctx):
                    try:
                        await func(session)
                        self.logger.info(f'Message {session.ctx["message_id"]} is handled as natural language by {func.__name__}.')
                    except Exception as e:
                        self.logger.exception(e)
                        self.logger.error(f'{type(e)} occured when {func.__name__} handling message {session.ctx["message_id"]}.')
                    return
            return nonebot.on_natural_language(keywords, **kwargs)(wrapper)
        return deco


    def scheduled_job(self, *args, **kwargs) -> Callable:
        kwargs.setdefault('timezone', pytz.timezone('Asia/Shanghai'))
        kwargs.setdefault('misfire_grace_time', 60)
        kwargs.setdefault('coalesce', True)
        def deco(func:Callable[[], Any]) -> Callable:
            @wraps(func)
            async def wrapper():
                try:
                    self.logger.info(f'Scheduled job {func.__name__} start.')
                    await func()
                    self.logger.info(f'Scheduled job {func.__name__} completed.')
                except Exception as e:
                    self.logger.exception(e)
                    self.logger.error(f'{type(e)} occured when doing scheduled job {func.__name__}.')
            return nonebot.scheduler.scheduled_job(*args, **kwargs)(wrapper)
        return deco


    async def broadcast(self, msgs, TAG='', interval_time=0.5, randomiser=None):
        bot = self.bot
        if isinstance(msgs, str):
            msgs = (msgs, )
        glist = await self.get_enable_groups()
        for gid, selfids in glist.items():
            try:
                for msg in msgs:
                    await asyncio.sleep(interval_time)
                    msg = randomiser(msg) if randomiser else msg
                    await bot.send_group_msg(self_id=random.choice(selfids), group_id=gid, message=msg)
                if l := len(msgs):
                    self.logger.info(f"群{gid} 投递{TAG}成功 共{l}条消息")
            except Exception as e:
                self.logger.exception(e)
                self.logger.error(f"群{gid} 投递{TAG}失败 {type(e)}")


__all__ = ('Service', 'Privilege')
