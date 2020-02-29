# HoshinoBot

A qqbot for Princess Connect Re:Dive (and other usage :)

## 简介

**HoshinoBot:** 基于[nonebot](http://nonebot.cqp.moe)框架，开源、无公害、非转基因的QQ机器人。



## 功能介绍

下面是本bot支持的功能

输入冒号后的文本即可使用

※@bot表明该功能必须at本bot才会触发

※请将说明中的所有`_`号替换为空格

※开启/关闭功能限群管理操作

### 公主连接 Re:Dive

- 转蛋模拟：@bot来发十连 或 @bot来发单抽
- 查看模拟卡池：看看卡池
- 竞技场查询：怎么拆_布丁_饭团_兔子_小仓唯

- rank推荐表：日服rank表 或 台服rank表

- 常用网址：pcr速查

- 会战管理（请见github.com/Ice-Cirno/HoshinoBot/tree/master/hoshino/modules/priconne/clanbattle）

- プリコネ官方四格查阅：@bot官漫123

+ プリコネ官方四格推送（默认开启）

### 蜜柑番剧

* 启用本模块：开启_bangumi

- 查看最近更新：@bot来点新番

+ 番剧推送（开启本模块后自动启用）

### 艦これ

+ 演习时间提醒：开启_kc-reminder

+ 时报：开启_hourcall

### 通用

- 查看本群启用的功能：服务列表

- 启用功能：启用_service-name

- 禁用功能：禁用_service-name

- 机器翻译（限群管理使用）： 翻译_もう一度、キミとつながる物語

- 联系作者：@bot来杯咖啡_你的反馈内容



## 部署指南

> 本bot的部分功能需要静态图片资源和带有认证的api key，恕不能公开。  
> 若您自行搭建，可能需要另寻途径获取。  
> 受影响的功能及获取key的方法，见本节[更进一步]()部分

### 前提条件

部署bot前，请准备好以下基础设施：

- 1台服务器：常见VPS提供商的最低配置已足够，WinServer/Linux均可
- 1个QQ帐号：建议使用小号
- 酷Q Air/Pro：「无头 QQ 客户端」，发送图片、禁言等功能需要Pro版
- CoolQ HTTP API 插件：详见https://cqhttp.cc/docs/
- Python 3.8：底层框架需>=3.7，本项目可有可无地使用了Python 3.8语言特性

> **若您使用 Linux 服务器：**  
> 推荐使用 CoolQ HTTP API 的 Docker 镜像 [coolq/wine-coolq](https://hub.docker.com/r/coolq/wine-coolq/)  
> 该镜像为您配置好了wine，并已安装 **酷Q** 和 **CoolQ HTTP API 插件**  
> 您可以在https://cqhttp.cc/docs/4.14/#/Docker 找到详细的安装说明

### 部署步骤


0. 安装 Python 3.8

```bash
# Ubuntu or Debian
sudo apt install python38
```
> 若您的包管理工具（如`yum`）尚不支持`python38`，你可以尝试从源码安装。Google will help you greatly : )

1. 克隆本仓库并安装依赖包
```bash
git clone https://github.com/Ice-Cirno/HoshinoBot.git
cd HoshinoBot
python38 -m pip install -r requirements.txt
```

2. 编辑配置文件
```bash
cp config_sample.py config.py
nano config.py
```
> 配置文件内有相应注释，请根据您的实际配置填写
>
> 若您从未使用过 `vim` 编辑器，推荐使用 `nano` : )
3. 运行bot
```bash
python38 run.py
```

当您完成以上步骤后，您可以尝试在群内发送 `@bot 在？` 查看机器人的在线状态（注：`@bot`表示at机器人，请手动at，复制无效，下同），或尝试发送`pcr速查`。如果机器人向您正常回复，恭喜您，您已经搭建成功了！



### 更进一步

现在，机器人已经可以使用`会战管理`、`模拟抽卡(纯文字版)`等基本功能了。但还无法使用`竞技场查询`、`番剧订阅`、`推特转发`等功能。这是因为，这些功能需要对应的静态图片资源以及相应的api key。相应资源获取有难有易，您可以根据自己的需要去获取，或者[赞助我们](https://jq.qq.com/?wv=1027&k=55fGEgi)的服务器运营，即可邀请部署好的bot入群。

下面将会分别介绍资源与api key的获取方法：



#### 静态图片资源

> 发送图片的条件：  
> 1. 酷Q Pro版  
> 2. 将`config.py`中的`IS_CQPRO`设为`True`  
> 3. 静态图片资源

您可能希望看到更为精致的图片版结果，若希望机器人能够发送图片，首先需要您购买酷Q Pro版，其次需要静态图片资源，其中包括：

- 公主连接角色头像（来自 [干炸里脊资源站](https://redive.estertion.win/) 的拆包）
- 公主连接官方四格漫画
- 公主连接每月rank推荐表
- 表情包杂图
- setu库
- [是谁呼叫舰队](http://fleet.diablohu.com/)舰娘&装备页面截图
- 艦これ人事表

等资源。若自行收集可能较为困难，所以我们准备了一个较为精简的资源包以及下载脚本，可以满足公主连接相关功能的日常使用。如果需要，请加 **Hoshino的后花园** QQ群367501912 下载群文件。



#### pcrdfans授权key

竞技场查询功能的数据来自 [公主连结Re: Dive Fan Club - 硬核的竞技场数据分析站](https://pcrdfans.com/) ，查询需要授权key。您可以向pcrdfans的作者索要。（注：由于另一pcr机器人 [yobot](https://yobot.xyz/functions-3/) 的良好封装，带来了大量机器人搭建者，pcrdfans的作者最近常被打扰，我们**不建议**您因本项目而去联系他。推荐您前往网站[pcrdfans.com](https://pcrdfans.com)进行查询）

若您已有授权key，创建文件`hoshino/modules/priconne/arena/config.json`编写以下内容：

```json
{"AUTH_KEY": "your_auth_key"}
```



#### 蜜柑番剧 RSS Token

> 本功能属于`subscribe`模块，请在`config.py`的`MODULES_ON`中添加  
> 本功能默认关闭，在群内发送 "启用 bangumi" 即可开启

番剧订阅数据来自[蜜柑计划 - Mikan Project](https://mikanani.me/)，您可以注册一个帐号，添加订阅的番剧，之后点击Mikan首页的RSS订阅，复制类似于下面的url地址：

```
https://mikanani.me/RSS/MyBangumi?token=abcdfegABCFEFG%2b123%3d%3d
```

保留其中的`token`参数，创建文件`hoshino\modules\subscribe\mikan\config.json`编写以下内容：

```json
{"MIKAN_TOKEN" : "abcdfegABCFEFG+123=="}
```

注意：`token`中可能含有url转义，您需要将`%2b`替换为`+`，将`%3d`替换为`=`。



#### 晴乃词库

舰娘及装备查询功能使用了精简版的晴乃词库，如有需要请加QQ群[Hoshino的后花园](https://jq.qq.com/?wv=1027&k=55fGEgi)或联系晴乃维护组。



#### 时报文本

> 本功能属于`subscribe`模块，请在`config.py`的`MODULES_ON`中添加  
> 本功能默认关闭，在群内发送 "启用 hourcall" 即可开启

报时功能使用/魔改了艦これ中各个艦娘的报时语音，您可以在[舰娘百科](https://zh.kcwiki.org/wiki/舰娘百科)或[艦これ 攻略 Wiki](https://wikiwiki.jp/kancolle/)找到相应的文本/翻译，当然您也可以自行编写台词。在此，我们向原台词作者[田中](https://bbs.nga.cn/read.php?tid=9143913)[谦介](http://nga.178.com/read.php?tid=14045507)先生和他杰出的游戏作品表达诚挚的感谢！

若您已获取时报文本，创建文件`hoshino/modules/subscribe/hourcall/config.json`编写以下内容：

```json
{
    "HOUR_CALLS": [
        "HOUR_CALL_1",
        "HOUR_CALL_2"
    ],
    "HOUR_CALL_1": [
        "午夜零点", "〇一〇〇", "〇二〇〇", "〇三〇〇", "〇四〇〇", "〇五〇〇",
        "〇六〇〇", "〇七〇〇", "〇八〇〇", "〇九〇〇", "一〇〇〇", "一一〇〇",
        "一二〇〇", "一三〇〇", "一四〇〇", "一五〇〇", "一六〇〇", "一七〇〇",
        "一八〇〇", "一九〇〇", "二〇〇〇", "二一〇〇", "二二〇〇", "二三〇〇"
	],
    "HOUR_CALL_2": [
        "0","1","2","3","4","5","6","7","8","9","10","11","12",
        "13","14","15","16","17","18","19","20","21","22","23"
    ]
}    
```

您可以编入多组报时文本，机器人会按`HOUR_CALLS`中定义的顺序循环日替。



#### 推特转发

推特转发功能需要推特开发者帐号，具体申请方法请自行[Google](http://google.com)。注：现在推特官方大概率拒绝来自中国大陆的新申请，自备海外手机号及大学邮箱可能会帮到您。

若您已有推特开发者帐号，创建文件`hoshino/modules/subscribe/twitter/config.json`编写以下内容：

```json
{
    "consumer_key": "your_consumer_key",
    "consumer_secret": "your_consumer_secret",
    "access_token_key": "your_access_token_key",
    "access_token_secret": "your_access_token_secret"
}
```







## 友情链接

**干炸里脊资源站**: https://redive.estertion.win/

**公主连结Re: Dive Fan Club - 硬核的竞技场数据分析站**: https://pcrdfans.com/

**yobot**: https://yobot.xyz/functions-3/

