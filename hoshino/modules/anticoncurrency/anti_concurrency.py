import datetime
from functools import wraps

from hoshino import Service, priv, trigger
from hoshino.typing import CQEvent
from . import Process_Monitor

"""
在下面的列表中填入不希望机器人并发执行的指令, 这些指令只有等其中某个被完毕执行完毕才能开始执行另外一个
例: ANTI_CONCURRENCY_GROUPS = [['猜头像', '猜角色', 'cygames']]
    
支持设置多组反并发, 
如: ANTI_CONCURRENCY_GROUPS = [['猜头像', '猜角色'], ['完美配对', '神经衰弱']]
表示"猜头像"指令不能和"猜角色"指令并发, "完美配对"指令不能和"神经衰弱"指令并发
"""
ANTI_CONCURRENCY_GROUPS = [['猜头像', '猜角色', 'cygames', '猜群友', '猜语音', '完美配对', '神经衰弱']]
# 是否允许同一条指令自己和自己并发
SELF_CONCURRENCY = True
# HoshinoBot的触发器字典，一般不用修改
HOSHINO_TRIGGER_DICTS = [trigger.prefix.trie, trigger.suffix.trie, trigger.keyword.allkw, trigger.rex.allrex]

sv_help = '''
防止某些插件并发执行
'''.strip()

sv = Service(
    name='反并发',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # False隐藏
    enable_on_default=True,  # 是否默认启用
    bundle='通用',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助-反并发"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


process_status_dict = {}


def is_list_generated_by_one_element(list_, element):
    return element in list_ and len(set(list_)) == 1


def sf_wrapper(func, trigger_group_index, trigger_word):
    @wraps(func)
    async def wrapper(bot, ev: CQEvent):
        if process_status_dict.get((ev.group_id, trigger_group_index)):
            if not SELF_CONCURRENCY or (SELF_CONCURRENCY and not is_list_generated_by_one_element(
                    process_status_dict[(ev.group_id, trigger_group_index)], trigger_word)):
                await bot.send(ev, '要、要同时执行这么多指令吗? 呜, 晕头转向了...做不到')
                sv.logger.info('由于检测到未执行完的同组指令, 消息已被anti-concurrency插件自动忽略')
                return
        with Process_Monitor(ev.group_id, trigger_group_index, trigger_word, process_status_dict) as pm:
            return await func(bot, ev)

    return wrapper


async def add_trigger_words_wrapper():
    for trigger_group_index, trigger_group in enumerate(ANTI_CONCURRENCY_GROUPS):
        for trigger_word in trigger_group:
            for trigger_words_dict in HOSHINO_TRIGGER_DICTS:
                if trigger_word in trigger_words_dict:
                    sf = trigger_words_dict[trigger_word]
                    sf.func = sf_wrapper(sf.func, trigger_group_index, trigger_word)
                    sv.logger.info(f'Succeed to add wrapper on trigger `{trigger_word}`')
                    break


@sv.scheduled_job('date', next_run_time=datetime.datetime.now())
async def add_trigger_words_wrapper_job():
    await add_trigger_words_wrapper()
