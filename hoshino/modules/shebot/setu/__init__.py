from nonebot import MessageSegment
import os
import asyncio
import time
import json
import traceback
import nonebot

from queue import Queue
from .api import get_final_setu,get_final_setu_async
from .data_source import SetuWarehouse,add_to_delete,get_random_pic,save_config,load_config,send_setus
import re
import threading 
from .config import *
from service import Service,Priv

g_is_online = DEFAULT_ONLINE
g_with_url = WITH_URL

g_config = load_config()
g_r18_groups = set(g_config.get('r18_groups',[]))
g_delete_groups = set(g_config.get('delete_groups',[]))

g_msg_to_delete = {}

#初始化色图仓库
nr18_path = NR_PATH #存放非r18图片
r18_path = R18_PATH#存放r18图片
search_path = SEARCH_PATH #存放搜索图片
if not os.path.exists(search_path):
    os.mkdir(search_path)
wh = SetuWarehouse(nr18_path)
r18_wh = SetuWarehouse(r18_path,r18=1)

#启动一个线程一直补充色图
print('线程启动')
thd = threading.Thread(target=wh.keep_supply)
thd.start()

#启动一个线程一直补充r18色图
print('r18线程启动')
thd_r18 = threading.Thread(target=r18_wh.keep_supply)
thd_r18.start()

config_path = os.path.dirname(__file__)+'/config.json'
help_path = os.path.dirname(__file__)+'/help.txt'
sv = Service('涩图',config_path,help_path,default_enable=True)
@sv.on_message()
async def _(bot,ctx):
    global g_msg_to_delete
    message = ctx['raw_message']
    uid = ctx['user_id']
    gid = ctx.get('group_id',0)
    user_priv = sv.get_user_priv(ctx)
    is_to_delete = True if gid in g_delete_groups else False
    print(f'当前群：{gid}')
    print(f'当前用户:{uid}')

    if sv.is_black_user(uid):
        await bot.send(ctx,'您请求太频繁了，请过会再来')
        return 
    
    if COMMON_RE.match(message):
        if not g_is_online:
            print('发送本地涩图')
            pic = get_random_pic(nr18_path)
            folder = nr18_path.split('/')[-1]
            pic = f'[CQ:image,file={folder}/{pic}]'
            ret = await bot.send(ctx,pic)
            msg_id = ret['message_id']
            if is_to_delete:
                add_to_delete(msg_id,g_msg_to_delete) #30秒后删除
            return

        robj = COMMON_RE.match(message)
        try:
            num = int(robj.group(1))
        except:
            num = 1
        keyword = robj.group(2)
        if keyword:
            print(f"含有关键字{keyword}")
            if user_priv < Priv.SUPER:
                sv.add_black_user(uid,60)
                setus = await get_final_setu_async(search_path,keyword=keyword,r18=0)
            else:
                setus = await get_final_setu_async(search_path,keyword=keyword,r18=2) 
            await send_setus(bot,ctx,search_path,setus,g_with_url,is_to_delete,g_msg_to_delete)

        else:
            setus = wh.fetch(num)
            if not send_setus:#send_setus为空
                await bot.send(ctx,'色图库正在补充，下次再来吧',at_sender=False)
            else:
                await send_setus(bot,ctx,nr18_path,setus,g_with_url,is_to_delete,g_msg_to_delete)
            if num>1:
                sv.add_black_user(uid,10)

    elif SECRET_RE.match(message):
        if gid not in g_r18_groups and gid!= 0:
            await bot.send(ctx,'本群未开启r18色图，请私聊机器人,但注意不要过分请求，否则拉黑')
            return

        if not g_is_online:
            print('发送本地涩图')
            pic = get_random_pic(r18_path)
            folder = r18_path.split('/')[-1]
            pic = f'[CQ:image,file={folder}/{pic}]'
            ret = await bot.send(ctx,pic)
            msg_id = ret['message_id']
            if is_to_delete:
                add_to_delete(msg_id,g_msg_to_delete)
            return   

        try:
            num = int(SECRET_RE.match(message).group(1))
        except:
            num = 1
        if sv.get_user_priv(ctx) < Priv.PY:
            num = 1

        setus = r18_wh.fetch(num)
        print("发送r18")
        await send_setus(bot,ctx,r18_path,setus,g_with_url,is_to_delete,g_msg_to_delete)
        if user_priv < Priv.PY:
            sv.add_black_user(uid,10)
    else:
        print('无关消息')

@sv.on_message()
async def switch(bot,ctx):
    global g_is_online
    global g_delete_groups
    global g_config
    global g_r18_groups
    msg = ctx['raw_message']
    gid = ctx['group_id']
    if sv.get_user_priv(ctx) < Priv.SUPER:
        return
    if msg == '选择在线涩图':
        g_is_online = True
        await bot.send(ctx,'已选择在线涩图',at_sender=True)
    elif msg == '选择本地涩图':
        g_is_online = False
        await bot.send(ctx,'已选择本地涩图',at_sender=True)

    elif msg == '本群涩图撤回':
        g_delete_groups.add(gid)
        g_config['delete_groups'] = list(g_delete_groups)
        save_config(g_config)
        await bot.send(ctx,'本群涩图撤回',at_sender=True)

    elif msg == '本群涩图不撤回':
        g_delete_groups.discard(gid)
        g_config['delete_groups'] = list(g_delete_groups)
        save_config
        await bot.send(ctx,'本群涩图不撤回',at_sender=True)

    elif re.match(r'群(\d{5,12})?涩图撤回',msg):
        gid = int(re.match(r'群(\d{5,12})?涩图撤回',msg).group(1))
        g_delete_groups.add(gid)
        g_config['delete_groups'] = list(g_delete_groups)
        save_config(g_config)
        await bot.send(ctx,f'群{gid}涩图撤回')

    elif re.match(r'群(\d{5,12})?涩图不撤回',msg):
        gid = int(re.match(r'群(\d{5,12})?涩图不撤回',msg).group(1))
        g_delete_groups.discard(gid)
        g_config['delete_groups'] = list(g_delete_groups)
        save_config(g_config)
        await bot.send(ctx,f'群{gid}涩图不撤回')

    elif msg == '本群r18开启':
        g_r18_groups.add(gid)
        g_config['r18_groups'] = list(g_r18_groups)
        save_config(g_config)
        await bot.send(ctx,'本群r18开启',at_sender=True)

    elif msg == '本群r18关闭':
        g_r18_groups.discard(gid)
        g_config['r18_groups'] = list(g_r18_groups)
        save_config(g_config)
        await bot.send(ctx,'本群r18关闭',at_sender=True)

    elif re.match(r'群(\d{5,12})r18开启',msg):
        gid = int(re.match(r'群(\d{5,12})r18开启',msg).group(1))
        g_r18_groups.add(gid)
        g_config['r18_groups'] = list(g_r18_groups)
        save_config(g_config)
        await bot.send(ctx,f'群{gid}r18开启')

    elif re.match(r'群(\d{5,12})r18关闭',msg):
        gid = int(re.match(r'群(\d{5,12})r18关闭',msg).group(1))
        g_r18_groups.discard(gid)
        g_config['r18_groups'] = list(g_r18_groups)
        save_config(g_config)
        await bot.send(ctx,f'群{gid}r18关闭')

    else:
        pass

bot = nonebot.get_bot()
@bot.on_message
async def del_msg(ctx):
    self_id = ctx['self_id']
    global g_msg_to_delete
    print(g_msg_to_delete)
    try:
        if g_msg_to_delete == {}:
            return
        for msg_id in list(g_msg_to_delete.keys()):
            del_time = g_msg_to_delete.get(msg_id)
            if del_time:
                if time.time() > g_msg_to_delete[msg_id]:
                    del g_msg_to_delete[msg_id]
                    await bot.delete_msg(self_id=self_id,message_id=msg_id)
                    print('撤回一条消息')
    except:
        traceback.print_exc()




            
        

            
