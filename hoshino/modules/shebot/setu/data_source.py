import random
import asyncio
import os
import json
import datetime
from PIL import Image
from io import BytesIO
from .api import get_final_setu
from queue import Queue
import time

class SetuWarehouse:
    def __init__(self,store_path,r18=0):
        self.warehouse = Queue(4)
        self.r18 = r18
        if os.path.exists(store_path):
            self.store_path = store_path
        else:
            try:
                os.mkdir(store_path)
                self.store_path = store_path
            except Exception as ex:
                print(ex)

    def count(self):
            return self.warehouse.qsize()

    def keep_supply(self):
        while True:
            print('正在补充色图')
            setus = get_final_setu(num=8,storePath=self.store_path,r18=self.r18)
            for setu in setus:
                self.warehouse.put(setu)
                print(f'补充一张色图，库存{self.count()}张\n')

    def fetch(self,num=1): 
        send_pics=[]
        for i in range(0,num):
            try:
                send_pics.append(self.warehouse.get())
            except:
                print('色图不足，等待补充,本次取出取消')
            print(f'库存{self.count()}张\n')

        return send_pics

def extract_file_md5(raw_message):
    try:
        lis=raw_message.split(',')
        md5 = lis[1].split('.')[0].split('=')[1]
        return md5
    except Exception as ex:
        print(ex)

def get_random_pic(path):
    files = os.listdir(path)
    rfile = random.sample(files,1)[0]
    print(f'随机选择图片{rfile}')
    return rfile

def add_to_delete(msg_id:int,to_delete:dict):
        to_delete[msg_id] = time.time() + 30


path = os.path.join(os.path.dirname(__file__),'setu_config.json')
def save_config(config:dict):
    try:
        with open(path,'w',encoding='utf8') as f:
            json.dump(config,f,ensure_ascii=False,indent=2)
        return True
    except Exception as ex:
        print(ex)
        return False

def load_config():
    try:
        with open(path,'r',encoding='utf8') as f:
            config = json.load(f)
            return config
    except:
        return {}

async def send_setus(bot,ctx,setu_path,setus,with_url=False,is_to_delete=False,msgs_to_del={}):
    folder = setu_path.split('/')[-1]
    reply = ''
    for setu in setus:
        pic = f'[CQ:image,file={folder}/{setu.pid}]'
        reply += f'{setu.title}\n画师：{setu.author}\npid:{setu.pid}{pic}'
    ret = await bot.send(ctx,reply,at_sender=False)
    if with_url:
        urls = ''
        for setu in setus:
            urls = urls+setu.url+'\n\n'
        await bot.send(ctx,urls.strip(),at_sender=False)
    if is_to_delete:
        msg_id = ret['message_id']
        add_to_delete(msg_id,msgs_to_del)
    





                        
#asyncio.run(get_setu(IMGPATH,1))
