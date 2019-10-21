import re
import random

import nonebot
from nonebot import on_command, CommandSession, Message, CQHttpError
from nonebot.permission import *

#, permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER)

re_silence = re.compile(r'来.?份(.*)睡眠套餐')

@on_command('silence', aliases=('睡眠套餐', '休眠套餐', '精致睡眠', '来一份精致睡眠套餐', re_silence)) 
async def silence(session: CommandSession):
    group_id = session.ctx['group_id']
    user_id = session.ctx['user_id']
    await session.bot.set_group_ban(group_id=group_id , user_id=user_id, duration=8*60*60)


bot = nonebot.get_bot()
last_msg = {}
repeated_flag = {}
prob_n = 0.0
PROB_A = 1.6    # 由于下行所述的bug，暂时先提高复读概率，以减少被打断蓄力
# FIXME: 对不同群分别进行处理。现在的逻辑会使别的群打断当前群复读蓄力 
# ↑ FIXED at 20191011 by Ice-Cirno
'''
不复读率 随 复读次数 指数级衰减
从第2条复读，即第3条重复消息开始有几率触发复读

a 设为一个略大于1的小数，最好不要超过2，建议1.6
复读概率计算式：p_n = 1 - 1/a^n
递推式：p_n+1 = 1 - (1 - p_n) / a
'''
@bot.on_message('group')
async def random_repeater(context):
    global last_msg
    global repeated_flag
    global prob_n
    global PROB_A
    group_id = context['group_id']
    msg = context['message'].extract_plain_text().strip()
    if (group_id in last_msg) and (group_id in repeated_flag) and (last_msg[group_id] == msg):
        if not repeated_flag[group_id]:
            if random.random() < prob_n:    # 概率测试通过，复读并设flag
                try:
                    await bot.send(context, msg)
                    repeated_flag[group_id] = True
                except CQHttpError as e:
                    print(e)
                    print('复读失败: CQHttpError')
            else:                           # 蓄力
                prob_n = 1 - (1-prob_n)/PROB_A
    else:   # 不是复读，重置
        last_msg[group_id] = msg
        repeated_flag[group_id] = False
        prob_n = 0

    def p(a):
        '''
        该函数打印prob_n用于选取调节a
        注意：由于依指数变化，a的轻微变化会对概率有很大影响
        '''
        p0 = 0
        for _ in range(10):
            p0 = (p0 - 1) / a + 1
            print(p0)
