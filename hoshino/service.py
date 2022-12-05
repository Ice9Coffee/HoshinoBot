import asyncio
import os
import random
import re
from collections import defaultdict
from functools import wraps

import nonebot
import pytz
from nonebot.command import SwitchException, _FinishException, _PauseException
from nonebot.message import CanceledException, Message

import hoshino
from hoshino import log, priv, trigger
from hoshino.typing import *

try:
    import ujson as json
except:
    import json

# service management
_loaded_services: Dict[str, "Service"] = {}  # {name: service}
_service_bundle: Dict[str, List["Service"]] = defaultdict(list)
_re_illegal_char = re.compile(r'[\\/:*?"<>|\.]')
_service_config_dir = os.path.expanduser('~/.hoshino/service_config/')
os.makedirs(_service_config_dir, exist_ok=True)


def _load_service_config(service_name):
    config_file = os.path.join(_service_config_dir, f'{service_name}.json')
    if not os.path.exists(config_file):
        return {}  # config file not found, return default config.
    try:
        with open(config_file, encoding='utf8') as f:
            config = json.load(f)
            return config
    except Exception as e:
        hoshino.logger.exception(e)
        return {}


def _save_service_config(service):
    config_file = os.path.join(_service_config_dir, f'{service.name}.json')
    with open(config_file, 'w', encoding='utf8') as f:
        json.dump(
            {
                "name": service.name,
                "use_priv": service.use_priv,
                "manage_priv": service.manage_priv,
                "enable_on_default": service.enable_on_default,
                "visible": service.visible,
                "enable_group": list(service.enable_group),
                "disable_group": list(service.disable_group)
            },
            f,
            ensure_ascii=False,
            indent=2)


class ServiceFunc:
    def __init__(self, sv: "Service", func: Callable, only_to_me: bool, normalize_text: bool=False):
        self.sv = sv
        self.func = func
        self.only_to_me = only_to_me
        self.normalize_text = normalize_text
        self.__name__ = func.__name__

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class Service:
    """将一组功能包装为服务, 提供增强的触发条件与分群权限管理.

    支持的触发条件:
    `on_message`,
    `on_prefix`, `on_fullmatch`, `on_suffix`,
    `on_keyword`, `on_rex`,
    `on_command`, `on_natural_language`

    提供接口：
    `scheduled_job`, `broadcast`

    服务的配置文件格式为：
    {
        "name": "ServiceName",
        "use_priv": priv.NORMAL,
        "manage_priv": priv.ADMIN,
        "enable_on_default": true/false,
        "visible": true/false,
        "enable_group": [],
        "disable_group": []
    }

    储存位置：
    `~/.hoshino/service_config/{ServiceName}.json`
    """
    def __init__(self, name, use_priv=None, manage_priv=None, enable_on_default=None, visible=None,
                 help_=None, bundle=None):
        """
        定义一个服务
        配置的优先级别：配置文件 > 程序指定 > 缺省值
        """
        assert not _re_illegal_char.search(name), r'Service name cannot contain character in `\/:*?"<>|.`'

        config = _load_service_config(name)
        self.name = name
        self.use_priv = config.get('use_priv') or use_priv or priv.NORMAL
        self.manage_priv = config.get(
            'manage_priv') or manage_priv or priv.ADMIN
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
        self.help = help_
        self.enable_group = set(config.get('enable_group', []))
        self.disable_group = set(config.get('disable_group', []))

        self.logger = log.new_logger(name, hoshino.config.DEBUG)

        assert self.name not in _loaded_services, f'Service name "{self.name}" already exist!'
        _loaded_services[self.name] = self
        _service_bundle[bundle or "通用"].append(self)

    @property
    def bot(self):
        return hoshino.get_bot()

    @staticmethod
    def get_loaded_services() -> Dict[str, "Service"]:
        return _loaded_services

    @staticmethod
    def get_bundles():
        return _service_bundle

    def set_enable(self, group_id):
        self.enable_group.add(group_id)
        self.disable_group.discard(group_id)
        _save_service_config(self)
        self.logger.info(f'Service {self.name} is enabled at group {group_id}')

    def set_disable(self, group_id):
        self.enable_group.discard(group_id)
        self.disable_group.add(group_id)
        _save_service_config(self)
        self.logger.info(
            f'Service {self.name} is disabled at group {group_id}')

    def check_enabled(self, group_id):
        return bool((group_id in self.enable_group) or (self.enable_on_default and group_id not in self.disable_group))


    def _check_all(self, ev: CQEvent):
        gid = ev.group_id
        return self.check_enabled(gid) and not priv.check_block_group(gid) and priv.check_priv(ev, self.use_priv)

    async def get_enable_groups(self) -> dict:
        """获取所有启用本服务的群

        @return { group_id: [self_id1, self_id2] }
        """
        gl = defaultdict(list)
        for sid in hoshino.get_self_ids():
            try:
                sgl = await self.bot.get_group_list(self_id=sid)
            except CQHttpError:
                sgl = []
            sgl = set(g['group_id'] for g in sgl)
            if self.enable_on_default:
                sgl = sgl - self.disable_group
            else:
                sgl = sgl & self.enable_group
            for g in sgl:
                gl[g].append(sid)
        return gl


    def on_message(self, event='group') -> Callable:
        def deco(func) -> Callable:
            @wraps(func)
            async def wrapper(ctx):
                if self._check_all(ctx):
                    try:
                        return await func(self.bot, ctx)
                    except Exception as e:
                        self.logger.error(f'{type(e)} occured when {func.__name__} handling message {ctx["message_id"]}.')
                        self.logger.exception(e)
                    return
            return self.bot.on_message(event)(wrapper)
        return deco


    def on_prefix(self, *prefix, only_to_me=False) -> Callable:
        if len(prefix) == 1 and not isinstance(prefix[0], str):
            prefix = prefix[0]
        def deco(func) -> Callable:
            sf = ServiceFunc(self, func, only_to_me)
            for p in prefix:
                if isinstance(p, str):
                    trigger.prefix.add(p, sf)
                else:
                    self.logger.error(f'Failed to add prefix trigger `{p}`, expecting `str` but `{type(p)}` given!')
            return func
        return deco


    def on_fullmatch(self, *word, only_to_me=False) -> Callable:
        if len(word) == 1 and not isinstance(word[0], str):
            word = word[0]
        def deco(func) -> Callable:
            @wraps(func)
            async def wrapper(bot, event: CQEvent):
                if len(event.message) != 1 or event.message[0].data.get('text'):
                    self.logger.info(f'Message {event.message_id} is ignored by fullmatch condition.')
                    raise SwitchException(Message(event.raw_message))
                return await func(bot, event)
            sf = ServiceFunc(self, wrapper, only_to_me)
            for w in word:
                if isinstance(w, str):
                    trigger.prefix.add(w, sf)
                else:
                    self.logger.error(f'Failed to add fullmatch trigger `{w}`, expecting `str` but `{type(w)}` given!')
            return func
            # func itself is still func, not wrapper. wrapper is a part of trigger.
            # so that we could use multi-trigger freely, regardless of the order of decorators.
            # ```
            # @NO_DECO_HERE         # <- won't work
            # @on_keyword(...)
            # @on_fullmatch(...)    # you can change the order of `on_xx` decorators
            # @OTHER_DECO_HERE      # <- will work
            # async def func(...):
            #   ...
            # ```
        return deco


    def on_suffix(self, *suffix, only_to_me=False) -> Callable:
        if len(suffix) == 1 and not isinstance(suffix[0], str):
            suffix = suffix[0]
        def deco(func) -> Callable:
            sf = ServiceFunc(self, func, only_to_me)
            for s in suffix:
                if isinstance(s, str):
                    trigger.suffix.add(s, sf)
                else:
                    self.logger.error(f'Failed to add suffix trigger `{s}`, expecting `str` but `{type(s)}` given!')
            return func
        return deco


    def on_keyword(self, *keywords, only_to_me=False, normalize=True) -> Callable:
        if len(keywords) == 1 and not isinstance(keywords[0], str):
            keywords = keywords[0]
        def deco(func) -> Callable:
            sf = ServiceFunc(self, func, only_to_me, normalize)
            for kw in keywords:
                if isinstance(kw, str):
                    trigger.keyword.add(kw, sf)
                else:
                    self.logger.error(f'Failed to add keyword trigger `{kw}`, expecting `str` but `{type(kw)}` given!')
            return func
        return deco


    def on_rex(self, rex: Union[str, re.Pattern], only_to_me=False, normalize=True) -> Callable:
        if isinstance(rex, str):
            rex = re.compile(rex)
        def deco(func) -> Callable:
            sf = ServiceFunc(self, func, only_to_me, normalize)
            if isinstance(rex, re.Pattern):
                trigger.rex.add(rex, sf)
            else:
                self.logger.error(f'Failed to add rex trigger `{rex}`, expecting `str` or `re.Pattern` but `{type(rex)}` given!')
            return func
        return deco


    def on_command(self, name, *, only_to_me=False, deny_tip=None, **kwargs) -> Callable:
        kwargs['only_to_me'] = only_to_me

        def deco(func) -> Callable:
            @wraps(func)
            async def wrapper(session):
                if session.ctx['message_type'] != 'group':
                    return
                if not self.check_enabled(session.ctx['group_id']):
                    self.logger.debug(
                        f'Message {session.ctx["message_id"]} is command of a disabled service, ignored.'
                    )
                    if deny_tip:
                        session.finish(deny_tip, at_sender=True)
                    return
                if self._check_all(session.ctx):
                    try:
                        ret = await func(session)
                        self.logger.info(
                            f'Message {session.ctx["message_id"]} is handled as command by {func.__name__}.'
                        )
                        return ret
                    except CanceledException:
                        raise _FinishException
                    except (_PauseException, _FinishException, SwitchException) as e:
                        raise e
                    except Exception as e:
                        self.logger.error(f'{type(e)} occured when {func.__name__} handling message {session.ctx["message_id"]}.')
                        self.logger.exception(e)
            return nonebot.on_command(name, **kwargs)(wrapper)
        return deco


    def on_natural_language(self, keywords=None, **kwargs) -> Callable:
        def deco(func) -> Callable:
            @wraps(func)
            async def wrapper(session: nonebot.NLPSession):
                if self._check_all(session.ctx):
                    try:
                        ret = await func(session)
                        self.logger.info(
                            f'Message {session.ctx["message_id"]} is handled as natural language by {func.__name__}.'
                        )
                        return ret
                    except CanceledException:
                        raise _FinishException
                    except (_PauseException, _FinishException, SwitchException) as e:
                        raise e
                    except Exception as e:
                        self.logger.error(f'{type(e)} occured when {func.__name__} handling message {session.ctx["message_id"]}.')
                        self.logger.exception(e)
            return nonebot.on_natural_language(keywords, **kwargs)(wrapper)
        return deco


    def scheduled_job(self, *args, **kwargs) -> Callable:
        kwargs.setdefault('timezone', pytz.timezone('Asia/Shanghai'))
        kwargs.setdefault('misfire_grace_time', 60)
        kwargs.setdefault('coalesce', True)
        def deco(func: Callable[[], Any]) -> Callable:
            @wraps(func)
            async def wrapper():
                try:
                    self.logger.info(f'Scheduled job {func.__name__} start.')
                    ret = await func()
                    self.logger.info(f'Scheduled job {func.__name__} completed.')
                    return ret
                except Exception as e:
                    self.logger.error(f'{type(e)} occured when doing scheduled job {func.__name__}.')
                    self.logger.exception(e)
            return nonebot.scheduler.scheduled_job(*args, **kwargs)(wrapper)
        return deco


    async def broadcast(self, msgs, TAG='', interval_time=0.5, randomizer=None):
        bot = self.bot
        if isinstance(msgs, (str, MessageSegment, Message)):
            msgs = (msgs, )
        groups = await self.get_enable_groups()
        for gid, selfids in groups.items():
            try:
                for msg in msgs:
                    await asyncio.sleep(interval_time)
                    msg = randomizer(msg) if randomizer else msg
                    await bot.send_group_msg(self_id=random.choice(selfids), group_id=gid, message=msg)
                l = len(msgs)
                if l:
                    self.logger.info(f"群{gid} 投递{TAG}成功 共{l}条消息")
            except Exception as e:
                self.logger.error(f"群{gid} 投递{TAG}失败：{type(e)}")
                self.logger.exception(e)


    def on_request(self, *events):
        def deco(func):
            @wraps(func)
            async def wrapper(session):
                if not self.check_enabled(session.event.group_id):
                    return
                return await func(session)
            return nonebot.on_request(*events)(wrapper)
        return deco
    
    
    def on_notice(self, *events):
        def deco(func):
            @wraps(func)
            async def wrapper(session):
                if not self.check_enabled(session.event.group_id):
                    return
                return await func(session)
            return nonebot.on_notice(*events)(wrapper)
        return deco



sulogger = log.new_logger('sucmd', hoshino.config.DEBUG)

def sucmd(name, force_private=True, **kwargs) -> Callable:
    kwargs['privileged'] = True
    kwargs['only_to_me'] = False
    def deco(func) -> Callable:
        @wraps(func)
        async def wrapper(session: CommandSession):
            if session.event.user_id not in hoshino.config.SUPERUSERS:
                return
            if force_private and session.event.detail_type != 'private':
                await session.send('> This command should only be used in private session.')
                return
            try:
                return await func(session)
            except CanceledException:
                raise _FinishException
            except (_PauseException, _FinishException, SwitchException):
                raise
            except Exception as e:
                sulogger.error(f'{type(e)} occured when {func.__name__} handling message {session.event.message_id}.')
                sulogger.exception(e)
        return nonebot.on_command(name, **kwargs)(wrapper)
    return deco
