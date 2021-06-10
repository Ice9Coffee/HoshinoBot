from hoshino import Service, R
import json
import asyncio
from os import path
from hoshino import aiorequests, priv
import time
import nonebot
from hoshino.priv import *
from PIL import Image
import random

messageLengthLimit = 0
push_uids = {}
push_times = {}
room_states = {}
all_user_name = {}
isOnChecking = False
bilibiliCookie = ''

sv_help = '''
- 订阅动态+空格+需要订阅的UID+空格
- 取消订阅动态+空格+需要取消订阅的UID
- 重新载入动态推送配置
'''.strip()

sv = Service(
    name='B站动态',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # False隐藏
    enable_on_default=True,  # 是否默认启用
    bundle='订阅',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助-B站动态"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


async def broadcast(msg, groups=None, sv_name=None):
    bot = nonebot.get_bot()
    # 当groups指定时，在groups中广播；当groups未指定，但sv_name指定，将在开启该服务的群广播
    svs = Service.get_loaded_services()
    if not groups and sv_name not in svs:
        raise ValueError(f'不存在服务 {sv_name}')
    if sv_name:
        enable_groups = await svs[sv_name].get_enable_groups()
        send_groups = enable_groups.keys() if not groups else groups
    else:
        send_groups = groups
    for gid in send_groups:
        try:
            await bot.send_group_msg(group_id=gid, message=msg)
            await asyncio.sleep(0.5)
        except Exception as e:
            sv.logger.info(e)


def getImageCqCode(path):
    return '[CQ:image,file={imgUrl}]'.format(imgUrl=path)


def getLimitedMessage(originMsg):
    if messageLengthLimit > 0 and len(originMsg) > messageLengthLimit:
        return originMsg[0:messageLengthLimit] + '……'
    else:
        return originMsg


async def loadConfig():
    global push_uids
    global push_times
    global room_states
    global messageLengthLimit
    global bilibiliCookie
    push_uids = {}
    push_times = {}
    room_states = {}
    config_path = path.join(path.dirname(__file__), 'config.json')
    with open(config_path, 'r', encoding='utf8')as fp:
        conf = json.load(fp)
        messageLengthLimit = conf['message_length_limit']
        keys = conf['uid_bind'].keys()
        for uid in keys:
            push_uids[uid] = conf['uid_bind'][uid]
            push_times[uid] = int(time.time())
        for uid in keys:
            room_states[uid] = False
    # 生成16位LIVE_BUVID，好像随机生成没事
    list2 = []
    for number in range(16):
        str2 = str(random.randint(0, 9))
        list2.append(str2)
    b = "".join(list2)
    bilibiliCookie = 'LIVE_BUVID=AUTO{random_id};'.format(random_id=b)
    await load_all_username()
    sv.logger.info('B站动态推送配置文件加载成功')


def saveConfig():
    config_path = path.join(path.dirname(__file__), 'config.json')
    with open(config_path, 'r+', encoding='utf8')as fp:
        conf = json.load(fp)
        keys = push_uids.keys()
        conf['uid_bind'].clear()
        for uid in keys:
            conf['uid_bind'][uid] = push_uids[uid]
        fp.seek(0)
        fp.truncate()
        fp.seek(0)
        json.dump(conf, fp, indent=4)


async def check_uid_exsist(uid):
    header = {
        'Referer': 'https://space.bilibili.com/{user_uid}/'.format(user_uid=uid)
    }
    try:
        resp = await aiorequests.get('http://api.bilibili.com/x/space/acc/info?mid={user_uid}'.format(user_uid=uid),
                                     headers=header, timeout=20)
        res = await resp.json()
        if res['code'] == 0:
            return True
        return False
    except Exception as e:
        sv.logger.info('B站用户检查发生错误 ' + e)
        return False


async def get_user_name(uid):
    header = {
        'Referer': 'https://space.bilibili.com/{user_uid}/'.format(user_uid=uid)
    }
    try:
        resp = await aiorequests.get('http://api.bilibili.com/x/space/acc/info?mid={user_uid}'.format(user_uid=uid),
                                     headers=header, timeout=20)
        res = await resp.json()
        return res['data']['name']
    except Exception as e:
        sv.logger.info('B站用户名获取发生错误 ' + e)
        return False


async def load_all_username():
    global all_user_name
    uids = push_uids.keys()
    for uid in uids:
        all_user_name[uid] = await get_user_name(uid)


@sv.on_prefix('订阅动态')
async def subscribe_dynamic(bot, ev):
    if push_uids == {}:
        await loadConfig()
    text = str(ev.message).strip()
    if not text:
        await bot.send(ev, "请按照格式发送", at_sender=True)
        return
    if not ' ' in text:  # 仅当前群组
        if not await check_uid_exsist(text):
            await bot.send(ev, '订阅失败：用户不存在')
            return
        if not text in push_uids:
            push_uids[text] = [str(ev.group_id)]
            room_states[text] = False
        else:
            if str(ev.group_id) in push_uids[text]:
                await bot.send(ev, '订阅失败：请勿重复订阅')
                return
            push_uids[text].append(str(ev.group_id))
            push_times[uid] = int(time.time())
    else:
        subUid = text.split(' ')[0]
        subGroup = text.split(' ')[1]
        if not await check_uid_exsist(subUid):
            await bot.send(ev, '订阅失败：用户不存在')
            return
        if not subUid in push_uids:
            push_uids[subUid] = [subGroup]
            room_states[subUid] = False
        else:
            if subGroup in push_uids[subUid]:
                await bot.send(ev, '订阅失败：请勿重复订阅')
                return
            push_uids[subUid].append(subGroup)
        push_times[subUid] = int(time.time())
    saveConfig()
    await bot.send(ev, '订阅成功')


@sv.on_prefix('取消订阅动态')
async def disubscribe_dynamic(bot, ev):
    if push_uids == {}:
        await loadConfig()
    text = str(ev.message).strip()
    if not text:
        await bot.send(ev, "请按照格式发送", at_sender=True)
        return
    if not ' ' in text:  # 仅当前群组
        sv.logger.info(text)
        sv.logger.info(push_uids.keys())
        if text in push_uids.keys():
            if str(ev.group_id) in push_uids[text]:
                if len(push_uids[text]) == 1:
                    push_uids.pop(text)
                else:
                    push_uids[text].remove(str(ev.group_id))
            else:
                await bot.send(ev, '取消订阅失败：未找到该订阅')
                return
        else:
            await bot.send(ev, '取消订阅失败：未找到该订阅')
            return
    else:
        subUid = text.split(' ')[0]
        subGroup = text.split(' ')[1]
        if subGroup == 'all':
            if subUid in push_uids:
                push_uids.pop(subUid)
            else:
                await bot.send(ev, '取消订阅失败：未找到该订阅')
                return
        elif subUid in push_uids:
            if subGroup in push_uids[subUid]:
                if len(push_uids[subUid]) == 1:
                    push_uids.pop(subUid)
                else:
                    push_uids[subUid].remove(subGroup)
            else:
                await bot.send(ev, '取消订阅失败：未找到该订阅')
                return
        else:
            await bot.send(ev, '取消订阅失败：未找到该订阅')
            return
    saveConfig()
    await bot.send(ev, '取消订阅成功')


@sv.scheduled_job('cron', minute='*/2')
async def check_bili_dynamic():
    global push_times
    global room_states
    global isOnChecking
    if isOnChecking:
        return
    isOnChecking = True
    if push_uids == {}:
        await loadConfig()
    uids = push_uids.keys()
    sv.logger.info('B站动态检查开始')
    for uid in uids:
        # if uid != "171818544":
        #    continue
        header = {
            'Referer': 'https://space.bilibili.com/{user_uid}/'.format(user_uid=uid)
        }
        try:
            resp = await aiorequests.get(
                'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={user_uid}'.format(
                    user_uid=uid), headers=header, timeout=20)
            res = await resp.json()
            cards = res['data']['cards']
            # cards=[res['data']['cards'][10]]
            for card in cards:
                sendCQCode = []
                userUid = card['desc']['user_profile']['info']['uid']
                # uname=card['desc']['user_profile']['info']['uname']
                uname = all_user_name[uid]
                timestamp = card['desc']['timestamp']
                if timestamp < push_times[uid]:
                    # sv.logger.info(uname+'检查完成')
                    break
                dynamicId = card['desc']['dynamic_id']
                dynamicType = card['desc']['type']
                if dynamicType == 2:  # 带图片动态
                    sendCQCode.append(uname)
                    sendCQCode.append('发表了动态：\n')
                    content = card['card']
                    contentJo = json.loads(content)
                    picturesCount = contentJo['item']['pictures_count']
                    trueContent = contentJo['item']['description']
                    trueContent = getLimitedMessage(trueContent)
                    sendCQCode.append(trueContent)
                    pictures = contentJo['item']['pictures']
                    if picturesCount > 0:
                        isBigPicture = False
                        firstPictureSize = [pictures[0]['img_width'], pictures[0]['img_height']]
                        if picturesCount >= 9:
                            isBigPicture = True
                            for i in range(9):
                                if pictures[i]['img_width'] != firstPictureSize[0] or pictures[i]['img_height'] != \
                                        firstPictureSize[1]:
                                    isBigPicture = False
                            if isBigPicture:
                                pictureSrcs = []
                                for i in range(9):
                                    pictureSrcs.append(pictures[i]['img_src'])
                                imgPath = await make_big_image(pictureSrcs, firstPictureSize, 9)
                                sendCQCode.append(getImageCqCode('file:///' + imgPath))
                        if picturesCount >= 6 and not isBigPicture:
                            isBigPicture = True
                            for i in range(6):
                                if pictures[i]['img_width'] != firstPictureSize[0] or pictures[i]['img_height'] != \
                                        firstPictureSize[1]:
                                    isBigPicture = False
                            if isBigPicture:
                                pictureSrcs = []
                                for i in range(6):
                                    pictureSrcs.append(pictures[i]['img_src'])
                                imgPath = await make_big_image(pictureSrcs, firstPictureSize, 6)
                                pictureSrcs = []
                                sendCQCode.append(getImageCqCode('file:///' + imgPath))
                                if picturesCount > 6:
                                    for i in range(7, picturesCount):
                                        pictureSrcs.append(pictures[i]['img_src'])
                                    for downPic in pictureSrcs:
                                        sendCQCode.append(getImageCqCode(downPic))
                        if not isBigPicture:
                            if picturesCount > 0 and picturesCount < 4:
                                pictureSrcs = []
                                for pic in pictures:
                                    pictureSrcs.append(pic['img_src'])
                                for downPic in pictureSrcs:
                                    sendCQCode.append(getImageCqCode(downPic))
                    sendCQCode.append('\nhttps://t.bilibili.com/{dynamicId}'.format(dynamicId=dynamicId))
                elif dynamicType == 4:  # 纯文字动态
                    sendCQCode.append(uname)
                    sendCQCode.append('发表了动态：\n')
                    content = card['card']
                    contentJo = json.loads(content)
                    trueContent = contentJo['item']['content']
                    trueContent = getLimitedMessage(trueContent)
                    sendCQCode.append(trueContent)
                    sendCQCode.append('\nhttps://t.bilibili.com/{dynamicId}'.format(dynamicId=dynamicId))
                elif dynamicType == 64:  # 文章
                    sendCQCode.append(uname)
                    sendCQCode.append('发布了文章：\n')
                    content = card['card']
                    contentJo = json.loads(content)
                    cvid = str(contentJo['id'])
                    title = contentJo['title']
                    summary = contentJo['summary']
                    coverImage = contentJo['image_urls'][0]
                    sendCQCode.append(title)
                    sendCQCode.append(getImageCqCode(coverImage))
                    sendCQCode.append('\n')
                    sendCQCode.append(summary)
                    sendCQCode.append('……')
                    sendCQCode.append('\nhttps://www.bilibili.com/read/cv{cvid}'.format(cvid=cvid))
                elif dynamicType == 8:  # 投稿视频
                    sendCQCode.append(uname)
                    sendCQCode.append('投稿了视频：\n')
                    bvid = card['desc']['bvid']
                    content = card['card']
                    contentJo = json.loads(content)
                    title = contentJo['title']
                    coverImage = contentJo['pic']
                    videoDesc = contentJo['desc']
                    sendCQCode.append(title)
                    sendCQCode.append('\n')
                    sendCQCode.append(getImageCqCode(coverImage))
                    sendCQCode.append('\n')
                    videoDesc = getLimitedMessage(videoDesc)
                    sendCQCode.append(videoDesc)
                    sendCQCode.append('\n')
                    sendCQCode.append('\nhttps://www.bilibili.com/video/{bvid}'.format(bvid=bvid))
                elif dynamicType == 1:  # 转发动态
                    sendCQCode.append(uname)
                    sendCQCode.append('转发了动态：\n')
                    content = card['card']
                    contentJo = json.loads(content)
                    currentContent = contentJo['item']['content']
                    sendCQCode.append(currentContent)
                    sendCQCode.append('\n')
                    originType = contentJo['item']['orig_type']
                    originContentJo = json.loads(contentJo['origin'])  #
                    if originType == 2:
                        originUser = originContentJo['user']['name']
                        sendCQCode.append('>>')
                        sendCQCode.append(originUser)
                        sendCQCode.append('：')
                        sendCQCode.append('\n')
                        originTrueContent = originContentJo['item']['description']
                        originTrueContent = getLimitedMessage(originTrueContent)
                        sendCQCode.append(originTrueContent)
                    elif originType == 4:
                        originUser = originContentJo['user']['name']
                        sendCQCode.append('>>')
                        sendCQCode.append(originUser)
                        sendCQCode.append('：')
                        sendCQCode.append('\n')
                        trueContent = originContentJo['item']['content']
                        trueContent = getLimitedMessage(trueContent)
                        sendCQCode.append(trueContent)
                    elif originType == 8:
                        bvid = card['desc']['origin']['bvid']
                        title = originContentJo['title']
                        coverImage = originContentJo['pic']
                        ownerName = originContentJo['owner']['name']
                        sendCQCode.append('>>')
                        sendCQCode.append(ownerName)
                        sendCQCode.append('的视频:')
                        sendCQCode.append(title)
                        sendCQCode.append('\n')
                        sendCQCode.append(getImageCqCode(coverImage))
                        sendCQCode.append('\n')
                        sendCQCode.append('>>')
                        sendCQCode.append(bvid)
                    elif originType == 64:
                        title = originContentJo['title']
                        cvid = str(originContentJo['id'])
                        ownerName = originContentJo['author']['name']
                        sendCQCode.append('>>')
                        sendCQCode.append(ownerName)
                        sendCQCode.append('的文章:')
                        sendCQCode.append(title)
                        sendCQCode.append('\n')
                        sendCQCode.append('>>cv')
                        sendCQCode.append(cvid)
                    else:
                        sendCQCode.append('>>暂不支持的源动态类型，请进入动态查看')
                    sendCQCode.append('\nhttps://t.bilibili.com/{dynamicId}'.format(dynamicId=dynamicId))
                else:
                    sendCQCode.append(uname)
                    sendCQCode.append('发表了动态：\n')
                    sendCQCode.append('暂不支持该动态类型，请进入原动态查看')
                    sendCQCode.append('\nhttps://t.bilibili.com/{dynamicId}'.format(dynamicId=dynamicId))
                    sv.logger.info('type={type},暂不支持此类动态')
                msg = ''.join(sendCQCode)
                if push_uids[uid][0] == 'all':
                    await broadcast(msg, sv_name='bili-dynamic')
                else:
                    await broadcast(msg, push_uids[uid])
                time.sleep(0.5)
            push_times[uid] = int(time.time())
        except Exception as e:
            sv.logger.info('B站动态检查发生错误 ' + e)
    sv.logger.info('B站动态检查结束')
    # 直播状态检查
    sv.logger.info('B站直播状态检查开始')
    for uid in uids:
        try:
            header = {
                'Referer': 'https://space.bilibili.com/{user_uid}/'.format(user_uid=uid),
                'Cookie': bilibiliCookie
            }
            resp = await aiorequests.get(
                'https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid={user_id}'.format(user_id=uid),
                headers=header, timeout=20)
            res = await resp.json()
            if res['data']['liveStatus'] == 1 and not room_states[uid]:
                room_states[uid] = True
                sendCQCode = []
                userName = all_user_name[uid]
                sendCQCode.append(userName)
                sendCQCode.append('开播了：\n')
                sendCQCode.append(res['data']['title'])
                sendCQCode.append('\n')
                sendCQCode.append(getImageCqCode(res['data']['cover']))
                sendCQCode.append('\n')
                sendCQCode.append(res['data']['url'])
                msg = ''.join(sendCQCode)
                if push_uids[uid][0] == 'all':
                    await broadcast(msg, sv_name='bili-dynamic')
                else:
                    await broadcast(msg, push_uids[uid])
            elif room_states[uid] and res['data']['liveStatus'] == 0:
                room_states[uid] = False
                sendCQCode = []
                userResp = await aiorequests.get(
                    'https://api.bilibili.com/x/space/acc/info?mid={user_id}'.format(user_id=uid), timeout=20)
                userRes = await userResp.json()
                userName = userRes['data']['name']
                sendCQCode.append(userName)
                sendCQCode.append('下播了')
                msg = ''.join(sendCQCode)
                if push_uids[uid][0] == 'all':
                    await broadcast(msg, sv_name='bili-dynamic')
                else:
                    await broadcast(msg, push_uids[uid])
            time.sleep(0.5)
        except Exception as e:
            sv.logger.info('B站直播检查发生错误 ' + e)
    sv.logger.info('B站直播状态检查结束')
    isOnChecking = False


async def make_big_image(image_urls, size, imageNum):
    dirPath = path.join(path.dirname(__file__), 'res', 'image')
    for url in image_urls:  # 下载全部图片
        imageResp = await aiorequests.get(url)
        image = await imageResp.content
        imgFilename = url.rsplit('/', 1)[1]
        imagePath = path.join(dirPath, imgFilename)
        with open(path.abspath(imagePath), 'wb') as f:
            f.write(image)
    if imageNum == 9:
        newImg = Image.new('RGB', (size[0] * 3, size[1] * 3), 255)
        currentImageCount = 0
        for y in range(3):
            for x in range(3):
                img = Image.open(path.join(dirPath, image_urls[currentImageCount].rsplit('/', 1)[1]))
                newImg.paste(img, (x * size[0], y * size[1]))
                currentImageCount += 1
        savePath = image_urls[0].rsplit('/', 1)[1].split('.')[0] + 'make.jpg'
        newImg.save(savePath)
        return savePath
    if imageNum == 6:
        newImg = Image.new('RGB', (size[0] * 3, size[1] * 2), 255)
        currentImageCount = 0
        for y in range(2):
            for x in range(3):
                img = Image.open(path.join(dirPath, image_urls[currentImageCount].rsplit('/', 1)[1]))
                sv.logger.info(path.join(dirPath, image_urls[currentImageCount].rsplit('/', 1)[1]))
                sv.logger.info(currentImageCount)
                newImg.paste(img, (x * size[0], y * size[1]))
                currentImageCount += 1
        savePath = path.join(dirPath, image_urls[0].rsplit('/', 1)[1].split('.')[0] + '_make.jpg')
        newImg.save(savePath)
        return savePath
    pass


@sv.on_fullmatch(('重新载入B站动态推送配置', '重新载入动态推送配置'))
async def reload_config(bot, ev):
    await loadConfig()
    await bot.send(ev, '成功重新载入配置')
