# HoshinoBot
[![License](https://img.shields.io/github/license/Ice-Cirno/HoshinoBot)](LICENSE)
![Python Version](https://img.shields.io/badge/python-3.8+-blue)
![Nonebot Version](https://img.shields.io/badge/nonebot-1.6.0%2B%2C%202.0.0---blue)
[![试用/赞助群](https://img.shields.io/badge/试用/赞助-Hoshinoのお茶会-brightgreen)](https://jq.qq.com/?_wv=1027&k=eYGgrL4A)
[![开发交流群](https://img.shields.io/badge/开发交流-Hoshinoの后花园-brightgreen)](https://jq.qq.com/?_wv=1027&k=wgirhYYQ)

A QQ-bot for Princess Connect Re:Dive based on [Nonebot](https://github.com/nonebot/nonebot)

<details>
  <summary>开发历史</summary>

- 2019.09.20 HoshinoBot诞生
- ... (待补充)
- **2020年8月2日0点，qq机器人框架相继停止维护。** **感谢 酷Q项目 和 CQHTTP插件 的开发者们！感谢他们让Hoshino得以诞生！** **Hoshino不再对酷Q进行支持**

</details>


## 简介

**HoshinoBot:** 基于 [nonebot](https://docs.nonebot.dev/) 框架，开源、无公害、非转基因的QQ机器人。



## 功能介绍

HoshinoBot 的功能开发以服务 [公主连结☆Re:Dive](http://priconne-redive.jp) 玩家为核心。

<details>
  <summary>主要功能</summary>

- **转蛋模拟**：单抽、十连、抽一井
- **竞技场解法查询**：支持按服务器过滤，支持反馈点赞点踩
- **竞技场结算提醒**
- **公会战管理**：详细说明见[此文档](hoshino/modules/pcrclanbattle/clanbattle/README.md)
- **Rank推荐表搬运**
- **常用网址速查**
- **官方推特转发**
- **官方四格推送**
- **角色别称转换**
- **切噜语编解码**：切噜～♪
- **竞技场余矿查询**

> 由于bot的功能会快速迭代开发，使用方式这里不进行具体的说明，请向bot发送"help"或移步[此文件](hoshino/modules/botmanage/help.py)查看详细。会战管理功能的详细说明，请[点击这里](hoshino/modules/pcrclanbattle/clanbattle/README.md)

</details>

<details>
  <summary>通用功能</summary>

- **[蜜柑计划](http://mikanani.me)番剧更新订阅**
- **入群欢迎**&**退群提醒**
- **复读**
- **掷骰子**
- **精致睡眠套餐**
- **机器翻译**
- **反馈发送**：反馈内容将由bot私聊发送给维护组

</details>

此外，HoshinoBot 为 [艦隊これくしょん](http://www.dmm.com/netgame/feature/kancolle.html) 玩家开发了以下功能

<details>
  <summary>点击展开</summary>

- **官推转发**：「艦これ」開発/運営 & C2機関
- **时报**
- **演习时间提醒**
- **月度远征提醒**
- **舰娘信息查询**：`*晓改二`
- **装备信息查询**：`*震电改`
- **战果人事表查询**：`人事表191201`

> 艦これ相关功能由于个人精力实在有限，无法进行更多功能（如海图攻略）的开发/维护。
>
> 如果您有新的想法，欢迎联系我！即便您不会编程，您也可以在内容更新上帮到我们！

</details>

-------------

### 功能模块控制

HoshinoBot 的功能繁多，各群可根据自己的需要进行开关控制，群管理发送 `lssv` 即可查看功能模块的启用状态，使用以下命令进行控制：

```
启用 service-name
禁用 service-name
```


## 如何开始使用

QQ群[![试用/赞助群](https://img.shields.io/badge/试用/赞助-Hoshinoのお茶会-brightgreen)](https://jq.qq.com/?_wv=1027&k=eYGgrL4A)提供了我们部署的bot，提供Hoshino的原生服务。您可以在这里试用bot功能、赞助开发者，赞助者可邀请bot加入自己的群使用。

如果您具备基本的linux与python能力，并拥有一台服务器（轻量级即可），您可以参阅部署指南自行部署。


## 开源协议及免责声明

本项目遵守GPL-3.0协议开源，请在协议允许的条件及范围内使用本项目。本项目的开发者不会强制向您索要任何费用，同时也不会提供任何质保，一切因本项目引起的法律、利益纠纷由与本项目的开发者无关。
- 对于自行搭建、小范围私用的非营利性bot，若遇到任何部署、开发上的疑问，欢迎提交issue或加入[![开发交流群](https://img.shields.io/badge/开发交流-Hoshinoの后花园-brightgreen)](https://jq.qq.com/?_wv=1027&k=wgirhYYQ)讨论，我们欢迎有礼貌、描述详尽的提问！
- 对于以营利为目的部署的bot，由部署者负责，与本项目的开发者无关，本项目的开发者及社区没有义务回答您部署时的任何疑问。
- 对于HoshinoBot插件的开发者，在您发布插件或利用插件营利时，请遵守GPL-3.0协议将插件代码开源。

最终解释权归HoshinoBot开发组所有。



## 部署指南

**由于酷Q已停止运营，您可以使用[go-cqhttp](https://github.com/Mrs4s/go-cqhttp)或[CQHTTP Mirai](https://github.com/yyuueexxiinngg/cqhttp-mirai)作为无头QQ客户端。**

<details>
  <summary>（点击查看社区提供的部署指南）</summary>
> CentOS已停止更新，推荐使用Ubuntu 20.04或Debian。


- 《[使用 Docker 部署 HoshinoBot 与 yobot](https://cn.pcrbot.com/depoly-with-docker/)》作者：[yuudi](https://github.com/yuudi)

</details>

本bot功能繁多，部分功能需要静态图片资源和带有认证的api key，恕不能公开。本指南将首先带领您搭建具有**模拟抽卡(纯文字版)**、**会战管理v2**功能的HoshinoBot。其他功能需额外配置，请参考本章**更进一步**的对应小节。适用于日台服的**会战管理v3及v4版本**暂未开源，如有需要请前往[![试用/赞助群](https://img.shields.io/badge/试用/赞助-Hoshinoのお茶会-brightgreen)](https://jq.qq.com/?_wv=1027&k=eYGgrL4A)。

### 部署步骤

#### Windows 部署

1. 安装下面的软件/工具
    - Python 3.8：https://www.python.org/downloads/windows/
    - Git：https://git-scm.com/download/win
    - Notepad++：https://notepad-plus-plus.org/downloads/

2. 打开一个合适的文件夹，点击资源管理器左上角的 `文件 -> 打开Windows Powershell`

3. 输入以下命令克隆本仓库并安装依赖

    ```powershell
    git clone https://github.com/Ice-Cirno/HoshinoBot.git
    cd HoshinoBot
    py -3.8 -m pip install -r requirements.txt
    ```
    >若此处有报错信息，请务必解决，将错误信息复制到百度搜索一般即可找到解决办法。  
    >
    >若安装python依赖库时下载速度缓慢，可以尝试使用`py -3.8 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`

4. 回到资源管理器，进入`hoshino`文件夹，将`config_example`文件夹复制一份，重命名为`config`，然后右键使用Notepad++打开其中的`__bot__.py`，按照其中的注释说明进行编辑。

    > 如果您不清楚某项设置的作用，请保持默认。

5. 回到powershell，输入以下命令，启动 HoshinoBot

    ```powershell
    py -3.8 run.py
    ```

    > 若能看到日志`INFO: Running on 127.0.0.1:8080`，说明HoshinoBot启动成功。您可以忽略启动时的WARNING信息。如果出现ERROR，说明部分功能可能加载失败。

    至此，HoshinoBot的“大脑”已部署成功。接下来我们需要部署无头qq客户端，作为HoshinoBot的“口”和“耳”，收发消息。

6. 下载 go-cqhttp 至合适的文件夹

    - github 发布页：https://github.com/Mrs4s/go-cqhttp/releases

    > 您需要根据自己的机器架构选择版本，Windows一般为x86/64架构，通常选择[go-cqhttp_windows_386.exe](https://github.com/Mrs4s/go-cqhttp/releases/download/v1.0.0-rc1/go-cqhttp_windows_386.exe)

7. 在同文件夹内创建一个文本文件，重命名为`config.yml`，将以下内容写入文件：

    ```yaml
    account:
      uin: 你的机器人QQ号
      password: '' # 密码为空时使用扫码登录
      encrypt: false  # 是否开启密码加密
    heartbeat:
      interval: 5
    default-middlewares: &default
      access-token: ''
    database:
      leveldb:
        enable: true
    servers:
      - ws-reverse:
          universal: ws://127.0.0.1:8080/ws/
          reconnect-interval: 5000
          middlewares:
            <<: *default
    ```

    > 你需要在资源管理器上方菜单 -> 查看 -> 显示/隐藏 中勾选"文件扩展名"，以修改文件的后缀名。
    
    将其中的“你的机器人QQ号”替换为实际的QQ号，通常为8~11位纯数字。密码留空使用扫码登录，你也可以将密码写入配置文件，此时请妥善保存您的配置文件，不要泄露给其他人。
    
    > 关于go-cqhttp的配置，你可以在[这里](https://docs.go-cqhttp.org/guide/config.html#%E9%85%8D%E7%BD%AE%E4%BF%A1%E6%81%AF)找到更多说明。

8. 启动go-cqhttp，按照提示登录。

    登陆成功后，私聊机器人发送`在？`，若机器人有回复，恭喜您，您已经成功搭建起HoshinoBot了！

    之后您可以尝试在群内发送`!帮助`以查看会战管理的相关说明，发送`help`查看其他一般功能的相关说明，发送`pcr速查`查看常用网址等。
    
    注意，此时您的机器人功能还不完全，部分功能可能无法正常工作。若希望您的机器人可以发送图片，或使用其他进阶功能，请参考本章**更进一步**的对应小节。



#### Linux 部署

> CentOS已停止更新，推荐使用Ubuntu 20.04或Debian。

1. 安装 Python 3.8

    ```bash
    # Ubuntu or Debian
    sudo apt install python3.8
    ```

2. 克隆本仓库并安装依赖包
    ```bash
    git clone https://github.com/Ice-Cirno/HoshinoBot.git
    cd HoshinoBot
    python3.8 -m pip install -r requirements.txt
    ```

3. 编辑配置文件
    ```bash
    mv hoshino/config_example hoshino/config
    nano hoshino/config/__bot__.py
    ```
    > 配置文件内有相应注释，请根据您的实际配置填写，HoshinoBot仅支持反向ws通信
    >
    > 您也可以使用`vim`编辑器，若您从未使用过，我推荐您使用 `nano` : )

4. 运行HoshinoBot
    ```bash
    python3.8 run.py
    ```

    > 你需要在tmux或screen中运行。

5. 下载 go-cqhttp 至合适的文件夹

    - github 发布页：https://github.com/Mrs4s/go-cqhttp/releases

    > 您需要根据自己的机器架构选择版本，一般x86/64的Linux选择[go-cqhttp_linux_386.tar.gz](https://github.com/Mrs4s/go-cqhttp/releases/download/v1.0.0-rc1/go-cqhttp_linux_386.tar.gz)

6. 解压后，在`go-cqhttp`的同目录下创建配置文件`config.yml`，将以下内容写入文件：

    ```yaml
    account:
      uin: 你的机器人QQ号
      password: '' # 密码为空时使用扫码登录
      encrypt: false  # 是否开启密码加密
    heartbeat:
      interval: 5
    default-middlewares: &default
      access-token: ''
    database:
      leveldb:
        enable: true
    servers:
      - ws-reverse:
          universal: ws://127.0.0.1:8080/ws/
          reconnect-interval: 5000
          middlewares:
            <<: *default
    ```

    将其中的“你的机器人QQ号”替换为实际的QQ号，通常为8~11位纯数字。密码留空使用扫码登录，你也可以将密码写入配置文件，此时请妥善保存您的配置文件，不要泄露给其他人。

    > 关于go-cqhttp的配置，你可以在[这里](https://docs.go-cqhttp.org/guide/config.html#%E9%85%8D%E7%BD%AE%E4%BF%A1%E6%81%AF)找到更多说明。

7. 运行`go-cqhttp`，按照提示登录。

    登陆成功后，私聊机器人发送`在？`，若机器人有回复，恭喜您！您已经成功搭建起HoshinoBot了。之后您可以尝试在群内发送`!帮助`以查看会战管理的相关说明，发送`help`查看其他一般功能的相关说明，发送`pcr速查`查看常用网址等。

    注意，此时您的机器人功能还不完全，部分功能可能无法正常工作。若希望您的机器人可以发送图片，或使用其他进阶功能，请参考本章**更进一步**的对应小节。

### 更进一步

现在，机器人已经可以使用`会战管理`、`模拟抽卡(纯文字版)`等基本功能了。但还无法使用`竞技场查询`、`番剧订阅`、`推特转发`等功能。这是因为，这些功能需要对应的静态图片资源以及相应的api key。相应资源获取有难有易，您可以根据自己的需要去获取。

下面将会分别介绍资源与api key的获取方法：



#### 静态图片资源

您可能希望看到更为精致的图片版结果，若希望机器人能够发送图片，需要准备静态图片资源，其中包括：

- 公主连接官方四格漫画
- 公主连接每月rank推荐表
- 表情包杂图
- setu库
- [是谁呼叫舰队](http://fleet.diablohu.com/)舰娘&装备页面截图

等资源。自行收集可能较为困难，所以我们准备了一个较为精简的资源包以及下载脚本，可以满足公主连接相关功能的日常使用。如果需要，请加入QQ群 **Hoshino的后花园** 367501912，下载群文件中的`res.zip`。



#### pcrdfans授权key

竞技场查询功能的数据来自 [公主连结Re: Dive Fan Club - 硬核的竞技场数据分析站](https://pcrdfans.com/) ，查询需要授权key。您可以向pcrdfans的作者索要。（注：由于最近机器人搭建者较多，pcrdfans的作者最近常被打扰，我们**不建议**您因本项目而去联系他，推荐您前往网站[pcrdfans.com](https://pcrdfans.com)进行查询）

若您已有授权key，在文件`hoshino/config/priconne.py`中填写您的key：

```python
class arena:
    AUTH_KEY = "your_key"
```



#### 蜜柑番剧 RSS Token

> 请先在`hoshino/config/__bot__.py`的`MODULES_ON`中取消`mikan`的注释  
> 本功能默认关闭，在群内发送 "启用 bangumi" 即可开启

番剧订阅数据来自[蜜柑计划 - Mikan Project](https://mikanani.me/)，您可以注册一个账号，添加订阅的番剧，之后点击Mikan首页的RSS订阅，复制类似于下面的url地址：

```
https://mikanani.me/RSS/MyBangumi?token=abcdfegABCFEFG%2b123%3d%3d
```

保留其中的`token`参数，在文件`hoshino/config/mikan.py`中填写您的token：

```python
MIKAN_TOKEN = "abcdfegABCFEFG+123=="
```

注意：`token`中可能含有url转义，您需要将`%2b`替换为`+`，将`%2f`替换为`/`，将`%3d`替换为`=`。



#### 时报文本

> 请先在`hoshino/config/__bot__.py`的`MODULES_ON`中取消`hourcall`的注释  
> 本功能默认关闭，在群内发送 "启用 hourcall" 即可开启

报时功能使用/魔改了艦これ中各个艦娘的报时语音，您可以在[舰娘百科](https://zh.kcwiki.org/wiki/舰娘百科)或[艦これ 攻略 Wiki](https://wikiwiki.jp/kancolle/)找到相应的文本/翻译，当然您也可以自行编写台词。在此，我们向原台词作者[田中](https://bbs.nga.cn/read.php?tid=9143913)[谦介](http://bbs.nga.cn/read.php?tid=14045507)先生和他杰出的游戏作品表达诚挚的感谢！

若您已获取时报文本，在文件`hoshino/config/hourcall.py`中填写您的文本。

您可以编入多组报时文本，机器人会按`HOUR_CALLS_ON`中定义的顺序循环日替。



#### 推特转发

推特转发功能需要推特开发者账号，具体申请方法请自行[Google](http://google.com)。注：现在推特官方大概率拒绝来自中国大陆的新申请，自备海外手机号及大学邮箱可能会帮到您。

若您已有推特开发者账号，在文件`hoshino/config/twitter.py`中填写您的key：

```python
consumer_key = "your_consumer_key",
consumer_secret = "your_consumer_secret",
access_token_key = "your_access_token_key",
access_token_secret = "your_access_token_secret"
```



## 友情链接

**干炸里脊资源站**: https://redive.estertion.win/

**公主连结Re: Dive Fan Club - 硬核的竞技场数据分析站**: https://pcrdfans.com/

**yobot**: https://yobot.win/

