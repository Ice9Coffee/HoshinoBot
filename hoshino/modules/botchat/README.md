# **Botchat**
## **轻量语言库**
### 可自行变更语言库内容，本模块已经配置少量应答 

### 自行添加应答的格式如下：
- ### 分权限应答
```python
from hoshino import priv

@sv.on_fullmatch(('指令1', '指令2'), only_to_me=True)  #设置应答关键词，only_to_me配置是否需要@Bot
async def chat_a(bot, ev):
    if not priv.check_priv(ev, priv.ADMIN):  #检查关键词发送者是否为群管理及以上权限
        await bot.send(ev, 'A')  #若不是，则回复 A
    else:
        await bot.send(ev, 'B')  #若是，则回复 B
```
- ### 多元素应答
```python
- 发送图片 -
from hoshino import R

@sv.on_fullmatch('指令1')
async def chat_b(bot, ev):
    await bot.send(ev, R.img('A.jpg').cqcode)  #发送在 Resources/img/下的图片 A.jpg

- 发送语音 -
import os
from hoshino import R

@sv.on_fullmatch('指令1')
async def chat_c(bot, ev):
    path = 'C:/Resources/gacha/gacha_10.mp3'
    await bot.send(ev, f'[CQ:record,file=file:///{path}]')  #发送在 C:/Resources/gacha/下的语音 gacha_10.mp3

- @发送者 -
@sv.on_fullmatch('指令1')
async def chat_d(bot, ev):
    await bot.send(ev, 'A', at_sender=True)  #at_sender配置是否需要@发送者

- 禁言发送者 -
from hoshino import util

@sv.on_fullmatch('指令1')
async def chat_e(bot, ev):
    await bot.send(ev, 'B')
    await util.silence(ev, 60)  #禁言发送者，时间为60s

```

- ### 分时段应答
```python
import pytz
from datetime import datetime

tz = pytz.timezone('Asia/Shanghai')  #设定时区

@sv.on_fullmatch('指令1')
async def chat_f(bot, ev):
    now_hour=datetime.now(tz).hour
    if 0<=now_hour<6:
        await bot.send(ev, f'A') #在0~6点回复 A
    elif 6<=now_hour<10:
        await bot.send(ev, f'B') #在6~10点回复 B
    elif 21<=now_hour<24:
        await bot.send(ev, f'C') #在21~24点回复 C
    else:
        await bot.send(ev, f'D') #在上述时间之外回复 D
```

- ### 概率应答
```python
import random

@sv.on_fullmatch('指令1')
async def chat_g(bot, ev):
    if random.random() <= 0.20:  #20%的概率应答
        await bot.send(ev, 'A')
```

- ### 不同触发方式
```python
sv.on_fullmatch('指令1')  #在群聊中完整单独匹配关键字才会回复 A
async def chat_h(bot, ev):
    await bot.send(ev, f'A')

sv.on_keyword('指令2')  #在群聊中匹配到关键字就会回复 B
async def chat_i(bot, ev):
    await bot.send(ev, f'B')

sv.on_rex(r'[123]指令')  #在群聊中模糊匹配关键字
    await bot.send(ev, f'C')

- 例如 -
@sv.on_fullmatch('来点好康的')
async def chat_j(bot, ev):
    await bot.send(ev, R.img('A.jpg').cqcode)
@sv.on_keyword('色图')
async def chat_k(bot, ev):
    await bot.send(ev, R.img('B.jpg').cqcode)
@sv.on_rex(r'[涩瑟色]图')
    await bot.send(ev, R.img('C.jpg').cqcode)
{
    当群聊中有人发送“来点好康的”，Bot 会发送图 A，但发送“好康的”或“来点”均不会发送图 A；
    当群聊中有人发送“色图”，Bot 会发送图 B，同时发送“来点色图”或“色图摩多摩多”均会发送图 B；
    当群聊中有人发送“色图”，Bot 会发送图 C，同时发送“瑟图”或“涩图”均会发送图 C
}
```
- ### 随机应答
```python
sv.on_fullmatch('指令1')
async def chat_l(bot, ev):
    A_BC = R.img('abc/').path  #指定随机图片目录
    filelist = os.listdir(A_BC)
    path = None
    while not path or not os.path.isfile(path):
        filename = random.choice(filelist)
        path = os.path.join(A_BC, filename)
        pic = R.img('abc/', filename).cqcode
        await bot.send(ev, pic)
```