# -*- coding: utf-8 -*-

try:
    import ujson
except:
    import json as ujson

import aiofiles
# import aiohttp
from .constant import *
import os
import nonebot
import datetime
from dateutil.parser import parse
import random

# ——————————————————————————————————————————————————————————————————————————————

# Initialization constant
thesaurusReady = False
botQQ = 0

async def initialization():
    global thesaurusReady
    global botQQ
    bot = nonebot.get_bot()
    if thesaurusReady == False:
        botQQ = await bot.get_login_info()
        botQQ = int(botQQ['user_id'])
        thesaurusReady = True

# ——————————————————————————————————————————————————————————————————————————————

# Time operation
async def getTheCurrentTime():
    nowDate = str(datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d'))
    return nowDate

async def getAccurateTimeNow():
    nowDate = str(datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d/%H:%M:%S'))
    return nowDate

async def getTimeDifference(original, model = ALL):
    a = parse(original)
    b = parse(await getAccurateTimeNow())
    seconds = int((b - a).total_seconds())
    if model == ALL:
        return {
            DAY: int((b - a).days),
            HOUR: int(seconds / 3600),
            MINUTE: int((seconds % 3600) / 60), # The rest
            SECOND: int(seconds % 60) # The rest
        }
    if model == DAY:
        b = parse(await getTheCurrentTime())
        return int((b - a).days)
    if model == MINUTE:
        return int(seconds / 60)
    if model == SECOND:
        return seconds

async def timeToFile(path, time, parameter = 'default'):
    timeStructure = {
        parameter: str(time)
    }
    await writeJson(path, timeStructure)

async def timeReadFromFile(path, parameter = 'default'):
    return (await readJson(path))[parameter]
    
# ——————————————————————————————————————————————————————————————————————————————

# Common tools
async def atQQ(userQQ):
    return '[CQ:at,qq=' + str(userQQ) + ']\n'

async def cleanAt(msg):
    global botQQ
    atField = '[CQ:at,qq=' + str(botQQ) + ']'
    return msg.replace(atField, '').strip()

async def whetherAtBot(msg):
    global botQQ
    if msg.strip() == '[CQ:at,qq=' + str(botQQ) + ']':
        return True
    return False

async def randomListSelection(path, key):
    return random.choice((await readJson(path))[key])

async def checkFolder(path):
    dirPath = path[:path.rfind('/')]
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

async def randomlyExtractedFromTheFolder(path):
    try:
        return path + str(random.choice(os.listdir(path)))
    except:
        return FAILURE

async def authorityInspection(path, userQQ):
    content = await readJson(path)
    if content == FAILURE:
        return True
    for i in content['user']:
        if str(i) == str(userQQ):
            return True
    return False

# ——————————————————————————————————————————————————————————————————————————————

# json operation
async def readJson(p):
    if not os.path.exists(p):
        return FAILURE
    async with aiofiles.open(p, 'r', encoding='utf-8') as f:
        content = await f.read()
    content = ujson.loads(content)
    return content

async def writeJson(p, info):
    async with aiofiles.open(p, 'w', encoding='utf-8') as f:
        await f.write(ujson.dumps(info))
    return SUCCESS

# ——————————————————————————————————————————————————————————————————————————————

convenientParameterReadingAndWritingPath = ''

# Convenient parameter operation
async def parameterPathSetting(path):
    global convenientParameterReadingAndWritingPath
    convenientParameterReadingAndWritingPath = path

async def parameterReadingAndWriting(parameter, value = '', model = READ):
    global convenientParameterReadingAndWritingPath
    content = await readJson(convenientParameterReadingAndWritingPath)
    if model == READ:
        if content == FAILURE:
            return FAILURE
        return content[parameter]
    if model == WRITE:
        if content == FAILURE:
            # Check folder
            pathDirs = convenientParameterReadingAndWritingPath[:convenientParameterReadingAndWritingPath.rfind('/')]
            if not os.path.exists(pathDirs):
                os.makedirs(pathDirs)
            writeStructure = {
                parameter: value
            }
            await writeJson(convenientParameterReadingAndWritingPath, writeStructure)
        else:
            content[parameter] = value
            await writeJson(convenientParameterReadingAndWritingPath, content)

# ——————————————————————————————————————————————————————————————————————————————

# Match Command Tool
async def commandMatching(msg, commandList, model = ALL):
    backToCollection = {
        'mark': False,
        'command': ''
    }
    if model == ALL:
        for i in commandList:
            if msg.strip() == i:
                backToCollection['mark'] = True
                break
    if model == BLURRY:
        try:
            msgList = msg.strip().split(' ')
            for i in commandList:
                if i == msgList[0]:
                    backToCollection['command'] = msgList[1]
                    backToCollection['mark'] = True
                    break
        except:
            pass
    return backToCollection

# ——————————————————————————————————————————————————————————————————————————————

# Picture tool
async def pictureCqCode(relativePosition):
    relativePosition = relativePosition.strip('')
    back = relativePosition[relativePosition.find('/'):]
    filePath = os.path.dirname(__file__) + back
    return filePath
#    return '[CQ:image,file=' + filePath + ']'

# ——————————————————————————————————————————————————————————————————————————————


"""
# Network operation
async def asyncGet(url, headers = '', timeout = 10):
    if headers == '':
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url = url, headers = headers, timeout = timeout) as res:
                jsonStr = await res.json()
                return jsonStr
    except:
        return FAILURE 
"""
