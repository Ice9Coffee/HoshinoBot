import os
import re
from service import Service,Priv
from .data_source import save_record,load_records

RECORDS = load_records()

config_path = os.path.dirname(__file__)+'/config.json'
help_path = os.path.dirname(__file__)+'/help.txt' 
sv = Service('命令替换',config_path,help_path)

@sv.on_message()
async def add_replace(bot,ctx):
    global RECORDS
    uid = ctx['user_id']
    message = ctx['raw_message']
    user_priv = sv.get_user_priv(ctx)
    if user_priv < sv.manage_priv:
        return

    robj = re.match('(我|有人)问(.{1,100})你认为是(.{1,100})',message)
    if robj:
        is_open = True if robj.group(1)=='有人' else False
        old_msg = robj.group(2)
        new_msg = robj.group(3)
        RECORDS[old_msg] = {'new_msg':new_msg,'is_open':is_open,'rec_maker':uid}
        if save_record(RECORDS):
            await bot.send(ctx,'添加成功')
        else:
            await bot.send(ctx,'添加失败，请检查信息格式')
        return

    robj = re.match('(我|有人)问你认为是(.{1,200})(\[.{1,200}\])',message)
    if robj:
        is_open = True if robj.group(1)=='有人' else False
        old_msg = robj.group(3)
        new_msg = robj.group(2)
        RECORDS[old_msg] = {'new_msg':new_msg,'is_open':is_open,'rec_maker':uid}
        if save_record(RECORDS):
            await bot.send(ctx,'添加成功')
        else:
            await bot.send(ctx,'添加失败，请检查信息格式')
        return

    robj = re.match('删除替换(.{1,200})',message)
    if robj:
        old_msg = robj.group(1)
        del RECORDS[old_msg]
        save_record(RECORDS)
        await bot.send(ctx,'已删除替换',at_sender=True)
@sv.on_message('message.group')
async def replace(bot,ctx):
    uid = ctx['user_id']
    global RECORDS
    old_msg = ctx['raw_message']
    if old_msg not in RECORDS:
        return
    else:
        rec = RECORDS[old_msg]
        if not rec['is_open'] and uid != rec['rec_maker']:
            return
        else:
            ctx['raw_message'] = RECORDS[old_msg]['new_msg']

@sv.on_message()
async def show(bot,ctx):
    user_priv = sv.get_user_priv(ctx)
    if user_priv < Priv.PY:
        return
    message = ctx['message'].extract_plain_text().strip()
    if message == '查看替换':
        reply = ''
        for key in RECORDS:
                reply += (key+' : '+RECORDS[key]['new_msg']+'\n')
        await bot.send(ctx,reply.strip(),at_sender=False)

