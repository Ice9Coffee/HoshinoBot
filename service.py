import nonebot
import os
import json
import time
import traceback
import pytz
from functools import wraps

_loaded_services={} 

class Priv:
    BLACK = -1
    DEFAULT = 0
    NORMAL =1
    ADMIN = 10
    OWNER = 100
    PY = 101
    SUPER = 999
 
class Service:
    def __init__(self,name,config_path,help_path=None,need_priv=1,manage_priv=999,default_enable=True,
    allow_private=False,allow_group=True,is_visible=True,is_default_open=True):
        config = self._load_config(name,config_path)
        help_info = self._load_help(help_path)
        self.name = name
        self.config_path = config_path
        self.need_priv = config.get('need_priv',need_priv) 
        self.manage_priv = config.get('manage_priv',manage_priv) 
        self.default_enable = config.get('default_enable',default_enable) 
        self.enable = config.get('enable',default_enable) 
        self.enable_groups = set(config.get('enable_groups',[]))
        self.disable_groups = set(config.get('disable_groups',[]))
        self.allow_private = config.get('allow_private',allow_private) 
        self.allow_group = config.get('allow_group',allow_group) 
        self.is_visible = config.get('is_visible',is_visible)
        self.is_default_open = config.get('is_default_open',is_default_open)
        self.black_groups = config.get('black_groups',{})
        self.black_users = config.get('black_users',{})
        self.help = help_info

        _loaded_services[self.name] = self
            

    @property
    def bot(self):
        return nonebot.get_bot()

    def _load_config(self,name,config_path):
        if not os.path.exists(config_path):
            os.mknod(config_path)
            return {}
        try:
            with open(config_path,'r',encoding='utf8') as f:
                config = json.load(f)
                return config
        except Exception as ex:
            print(ex)
        return {}
    def _load_help(self,help_path):
        if not help_path:
            return None
        if not os.path.exists(help_path):
            return None
        try:
            with open(help_path,'r',encoding='utf8') as f: 
                data = f.read()
                f.close()
                return data
        except:
            traceback.print_exc()
            return None

    def _save_service_config(self):
        if not os.path.exists(self.config_path):
            print('配置文件路径不存在')
        try:
            print('尝试写入配置文件')
            with open(self.config_path,'w',encoding='utf8') as f:
                json.dump({
                        "need_priv" : self.need_priv,
                        "manage_priv" : self.manage_priv,
                        "enable_groups" : list(self.enable_groups),
                        "disable_groups": list(self.disable_groups),
                        "black_groups" : self.black_groups,
                        "black_users" : self.black_users,
                        "default_enable" : self.default_enable,
                        "enable" : self.enable,
                        "allow_private" : self.allow_private,
                        "allow_group" : self.allow_group
                },f,ensure_ascii=False,indent=2)
        except Exception as ex:
            print(ex)
            return

    def is_black_user(self,uid):
        if uid not in self.black_users:
            return False
        if uid in self.black_users and time.time()>self.black_users[uid]:
            del self.black_users[uid]
            self._save_service_config()
            return False
        return True

    def is_black_group(self,gid):
        if gid not in self.black_groups:
            return False
        if gid in self.black_groups and time.time()>self.black_groups[gid]:
            del self.black_groups[gid]
            self._save_service_config()
            return False
        return True

    def check_enable(self):
        return self.enable

    def check_group(self,ctx):
        group_id = ctx.get('group_id',0)
        if not self.allow_group:
            return False
        if group_id==0 and self.allow_private:#为私聊且允许私聊
            return True
        if not self.enable:
            return False
        if not self.is_default_open and group_id not in self.enable_groups:
            return False
        if self.is_default_open and group_id in self.disable_groups:
            return False
        if self.is_black_group(group_id):
            return False
        return True

    def check_user(self,ctx):
        user_priv = self.get_user_priv(ctx)
        if user_priv < self.need_priv:
            return False
        return True    

    def _check_all(self,ctx):
        return self.check_group(ctx) and self.check_user(ctx)
    
    def set_enable(self,ctx):
        if self.get_user_priv(ctx)<Priv.SUPER:
            return False
        self.enable = True
        self._save_service_config()
        return True
    
    def set_disable(self,ctx):
        if self.get_user_priv(ctx) <Priv.SUPER:
            return False
        self.enable = False
        self._save_service_config()
        return True

    def add_enable_group(self,gid,ctx):
        if self.get_user_priv(ctx) < self.manage_priv:
            return False
        self.enable_groups.add(gid)
        if gid in self.disable_groups:
            self.disable_groups.remove(gid)
        self._save_service_config()
        return True
    
    def add_disable_group(self,gid,ctx):
        if self.get_user_priv(ctx) < self.manage_priv:
            return False
        self.disable_groups.add(gid)
        if gid in self.enable_groups:
            self.enable_groups.remove(gid)
        self._save_service_config()
        return True

    def add_black_group(self,gid,last_time):
        self.black_groups[gid] = time.time()+last_time
        self._save_service_config()

    def add_black_user(self,uid,last_time):
        self.black_users[uid] = time.time()+last_time
        self._save_service_config()

    def get_user_priv(self,ctx):
        uid = ctx.get('user_id')
        bot = nonebot.get_bot()
        if uid in bot.config.SUPERUSERS:
            return Priv.SUPER
        if uid in bot.config.PYS:
            return Priv.PY
        if self.is_black_user(uid):
            return Priv.BLACK
        if ctx['message_type'] == 'group':
            if not ctx['anonymous']:
                role = ctx['sender'].get('role')
                if role == 'member':
                    return Priv.NORMAL
                elif role == 'admin':
                    return Priv.ADMIN
                elif role == 'owner':
                    return Priv.OWNER
            return Priv.NORMAL
        if ctx['message_type'] == 'private':
            return Priv.NORMAL

    @staticmethod
    def get_loaded_services():
        return _loaded_services

    def get_service_help(self):
        return self.help

    def on_message(self,event='message'):
        def deco(func):
            @wraps(func)
            async def wrapper(ctx):
                if self._check_all(ctx):
                    try:
                        await func(self.bot,ctx)
                    except:
                        traceback.print_exc()
                    return
            return self.bot.on(event)(wrapper)
        return deco

    def on_keyword(self,event='message',keywords=()):
        def deco(func):
            @wraps(func)
            async def wrapper(ctx):
                message = ctx['raw_message']
                for key in keywords:
                    if key in message:
                        if self._check_all(ctx):
                            try:
                                await func(self.bot,ctx)
                            except:
                                traceback.print_exc()
                            return  
                return                     
            return self.bot.on(event)(wrapper)
        return deco

    def scheduled_job(self, *args, **kwargs) :
        kwargs.setdefault('timezone', pytz.timezone('Asia/Shanghai'))
        kwargs.setdefault('misfire_grace_time', 60)
        kwargs.setdefault('coalesce', True)
        def deco(func) :
            @wraps(func)
            async def wrapper():
                try:
                    print(f'Scheduled job {func.__name__} start.')
                    await func()
                    print(f'Scheduled job {func.__name__} completed.')
                except:
                    traceback.print_exc()
            return nonebot.scheduler.scheduled_job(*args, **kwargs)(wrapper)
        return deco