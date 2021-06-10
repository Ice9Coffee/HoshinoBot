# -*- coding:utf-8 -*-
from hoshino import R
import os, json
import aiofiles


async def getIni(name, item):
    # 用R.img来操作ini文件是怎么一回事呢, 其实小编也不是很清楚, 可能只是单纯的想获取个path罢了.
    # 观众朋友们如果有什么想法欢迎在issue和小编讨论哦
    ini_path = R.img(f'image-generate/image_data/{name}/config.ini').path
    async with aiofiles.open(ini_path, "r", encoding="utf-8") as f:
        ini = await f.read()
    dic = json.loads(ini)
    return dic[item]


async def getQqName(uid):
    ini_path = R.img(f'image-generate/image_data/qqdata/{uid}.ini').path
    mark = "initial"
    if os.path.exists(ini_path):
        async with aiofiles.open(ini_path, "r", encoding="utf-8") as f:
            mark = await f.read()
            mark = mark.strip()
    return mark


async def setQqName(uid, msg):
    item = 0
    msg = str(msg)
    mark = str(await getQqName(uid))
    p = R.img(f"image-generate/image_data/qqdata/{uid}.ini").path
    name = R.img('image-generate/image_data/bieming/name.ini').path
    if os.path.exists(name):
        async with aiofiles.open(name, "r", encoding='utf-8') as f:
            line = await f.readlines()
            for i in line:
                i = i.strip()
                line_list = i.split(" ")
                if line_list[0] == msg:
                    mark = line_list[1]
                    item = 1
                    async with aiofiles.open(p, "w", encoding="utf-8") as f:
                        await f.write(str(mark))
                        return mark
