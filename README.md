# HoshinoBot

A qqbot for Princess Connect Re:Dive (and other usage :)


## 简介

**HoshinoBot:** 基于 [nonebot](http://nonebot.cqp.moe) 框架，开源、无公害、非转基因的QQ机器人。
此项目基于[Ice-Cirno](https://github.com/Ice-Cirno)的[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)，若您想搭建原版请从上面链接跳转，您也可以搭建这个版本。
Windows服务器部署本修改过的版本的难度在Linux服务器之上，若您使用的是Windows服务器，您可以直接看原版Hoshino。


## 功能介绍

请参照原版HoshinoBot。

## 部署指南

本bot功能繁多，部分功能需要静态图片资源和带有认证的api key，恕不能公开。本指南将首先带领您搭建具有**模拟抽卡(纯文字版)**、**会战管理**功能的HoshinoBot。其他功能需额外配置，请参考本章**更进一步**的对应小节。

### 部署步骤

### Windows部署
您可以尝试Windows部署本项目。

#### Linux 部署

我建议您在最开始就安装好Python 3.8

```bash
        # Ubuntu or Debian
        sudo apt install python3.8
```
若您的包管理工具（如`yum`）尚不支持`python3.8`，你可以尝试我写的一键编译安装Python的指令。  

```bash
    #境外CentOS/RHEL:
    yum -y update&&yum -y groupinstall "Development tools"&&yum -y install wget zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc* libffi-devel make git vim screen&&wget https://www.python.org/ftp/python/3.8.3/Python-3.8.3.tgz&&tar -zxvf Python-3.8.3.tgz&&cd Python-3.8.3&&./configure&&make&&make install&&pip3 install --upgrade pip&&cd
    #境内CentOS/RHEL:
    yum -y update&&yum -y groupinstall "Development tools"&&yum -y install wget zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc* libffi-devel make git vim screen&&wget http://npm.taobao.org/mirrors/python/3.8.3/Python-3.8.3.tgz&&tar -zxvf Python-3.8.3.tgz&&cd Python-3.8.3&&./configure&&make&&make install&&pip3 install --upgrade pip&&cd
```

##### 酷Q部署：
由于 酷Q 仅支持 Windows 环境，我们需要使用 docker 镜像来部署 酷Q 及 CQHTTP 插件。但别担心，相信我，这比 Windows 下部署更简单！您可以在[这个文档](https://cqhttp.cc/docs/)找到详细的说明。下面将带领您进行部署：

1. 安装 docker：若您的服务器是CentOS7，Debian或者Ubuntu，您可参考以下命令:

```bash
curl -sSL https://get.docker.com/ | sh
systemctl start docker
systemctl enable docker
```
如果您的系统是CentOS8，您可自行Google如何安装Docker :-D

2. 部署 docker：下面一条命令仅供参考，请根据实际情况修改参数；详细说明可见 [CQHTTP 文档 -> Docker](https://cqhttp.cc/docs/#/Docker)

    ```bash
    sudo docker run -d --name=hoshino \
    -v $(pwd)/coolq:/home/user/coolq \
    -p 9000:9000 --restart=always \
    -e VNC_PASSWD=MAXchar8 \
    -e COOLQ_ACCOUNT=10000 \
    -e COOLQ_URL=https://dlsec.cqp.me/cqp-full \
    -e CQHTTP_SERVE_DATA_FILES=no \
    -e CQHTTP_USE_HTTP=no \
    -e CQHTTP_USE_WS_REVERSE=yes \
    -e CQHTTP_WS_REVERSE_URL=ws://172.17.0.1:8080/ws/ \
    -e CQHTTP_WS_REVERSE_USE_UNIVERSAL_CLIENT=yes \
    richardchien/cqhttp:latest
    ```

    > 使用这行命令`ip addr show docker0 | grep -Po 'inet \K[\d.]+'`查看你的docker桥ip，替换`CQHTTP_WS_REVERSE_URL`中的链接
    >
    > 然后访问 `http://<你的IP>:9000/` 进入 noVNC（默认密码 `MAXchar8`），登录 酷Q
    > 
    > 注：如果你希望先使用酷Q Air进行尝试，请将COOLQ_URL设置为`https://dlsec.cqp.me/cqa-xiaoi`；之后可以用CQP.exe替换CQA.exe以升级，或删除容器重新创建。
    >
    >如果您希望这个httpapi插件以反向ws的方式接上cqpf的话，您可在上述命令加上一条:

```bash
    -e CQHTTP_USE_WS=yes \
```

##### Mirai部署：

mirai对Linux系统的支持非常好，若您希望通过mirai部署Hoshino，您可使用这些指令：
```bash
#若您的服务器是amd64构架
mkdir mirai&&cd mirai&&wget -c http://t.imlxy.net:64724/mirai/MiraiOK/miraiOK_linux_amd64 && chmod +x miraiOK* && ./miraiOK*
#若您的服务器不是amd64构架
mkdir mirai&&cd mirai&&wget -c http://t.imlxy.net:64724/mirai/MiraiOK/miraiOK_linux_arm64 && chmod +x miraiOK* && ./miraiOK*
```
Ctrl+C退出MiraiOK后当前目录下应该生成了plugins文件夹和mirai的一些文件，接下来我们使用以下指令：
```bash
#您需要了解vim编辑器的用法
cd plugins&&wget https://github.com/yyuueexxiinngg/cqhttp-mirai/releases/download/0.1.4/cqhttp-mirai-0.1.4-all.jar&&mkdir CQHTTPMirai&&cd CQHTTPMirai&&vim setting.yml
```
然后在setting.yml里，填入以下配置
```bash
"1234567890":
  ws_reverse:
    enable: true
    postMessageFormat: string
    reverseHost: 127.0.0.1
    reversePort: 8080
    reversePath: /ws/
    accessToken: null
    reconnectInterval: 3000
```
1234567890改成您用来当bot的QQ账号
详细说明请参考 https://github.com/yyuueexxiinngg/cqhttp-mirai
然后，
```bash
#使用screen创建一个窗口
screen -S mirai
cd ~/mirai&&./miraiOK*
# （mirai-console内）
login 123456789 ppaasswwdd
#最后使用Ctrl+a,d挂起这个shell
```

4. 克隆本仓库并安装依赖包
    ```bash
    cd&&git clone https://github.com/Chendihe4975/HoshinoBot.git
    cd HoshinoBot
    python3 -m pip install -r requirements.txt
    #安装扩展（可选）
    cd ~/HoshinoBot/hoshino/modules&&mkdir yobot&&cd yobot&&git init&&git clone https://github.com/yuudi/yobot.git&&cd ~/HoshinoBot/hoshino/modules&&mkdir custom&&cd custom&&git init&&git clone https://github.com/Lancercmd/Reloader.git&&git clone https://github.com/Lancercmd/Landsol-Distrust.git&&cd ~/HoshinoBot
    ```

5. 编辑配置文件
    ```bash
    mv hoshino/config_example hoshino/config
    vim hoshino/config/__bot__.py
    #按照注释填好，若您安装了扩展，您需要在_bot_.py取消custom和yobot的注释。
    #若您想开启yobot的web版公会战管理，您还需要将HOST改为0.0.0.0（默认是127.0.0.1）
    #若您没有安装扩展，您无需取消注释。
    ```
    > 配置文件内有相应注释，请根据您的实际配置填写，HoshinoBot仅支持反向ws通信
    >
    > 您需要了解Vim编辑器的用法
6. 运行bot
    ```bash
    #使用screen新建一个会话
    screen -S hoshino
    python3 run.py
    #若您安装了扩展，请在看到successed import yobot之后Ctrl+C先停止Hoshino
    vim ~/HoshinoBot/hoshino/modules/yobot/yobot/src/client/yobot_data/yobot_config.json
    #您需要把public_address中的9222改为8080
    #您完成以上修改之后，重新启动Hoshino
    python3 run.py
    #然后，您可用Ctrl+a,d挂起这个窗口
    ```
    若您按照正确的步骤部署，控制台应该会产生类似于这样的一条日志：
    ```bash
    [2020-07-17 15:50:26,435] 127.0.0.1:56363 GET /ws/ 1.1 101 - 7982
    ```
    
    私聊机器人发送`在？`，若机器人有回复，恭喜您！您已经成功搭建起HoshinoBot了。之后您可以尝试在群内发送`!帮助`以查看会战管理的相关说明，发送`help`查看其他一般功能的相关说明，发送`pcr速查`查看常用网址等。
    
    注意，此时您的机器人功能还不完全，部分功能可能无法正常工作。若希望您的机器人可以发送图片，或使用其他进阶功能，请参考本章**更进一步**的对应小节。



### 更进一步

现在，机器人已经可以使用`会战管理`、`模拟抽卡(纯文字版)`等基本功能了。但还无法使用`竞技场查询`、`番剧订阅`、`推特转发`等功能。这是因为，这些功能需要对应的静态图片资源以及相应的api key。相应资源获取有难有易，您可以根据自己的需要去获取。

下面将会分别介绍资源与api key的获取方法：



#### 静态图片资源

> 发送图片的条件：  
> 1. 酷Q Pro版  
> 2. 将`hoshino/config/__bot__.py`中的`USE_CQPRO`设为`True`  
> 3. 静态图片资源

您可能希望看到更为精致的图片版结果，若希望机器人能够发送图片，首先需要您购买酷Q Pro版，其次需要准备静态图片资源，其中包括：

- 公主连接角色头像（来自 [干炸里脊资源站](https://redive.estertion.win/) 的拆包）
- 公主连接官方四格漫画
- 公主连接每月rank推荐表
- 表情包杂图
- setu库
- [是谁呼叫舰队](http://fleet.diablohu.com/)舰娘&装备页面截图
- 艦これ人事表

等资源。自行收集可能较为困难，所以我们准备了一个较为精简的资源包以及下载脚本，可以满足公主连接相关功能的日常使用。如果需要，请加入QQ群 **Hoshino的后花园** 367501912，下载群文件中的`res.zip`。



#### pcrdfans授权key

竞技场查询功能的数据来自 [公主连结Re: Dive Fan Club - 硬核的竞技场数据分析站](https://pcrdfans.com/) ，查询需要授权key。您可以向pcrdfans的作者索要。（注：由于最近机器人搭建者较多，pcrdfans的作者最近常被打扰，我们**不建议**您因本项目而去联系他，推荐您前往网站[pcrdfans.com](https://pcrdfans.com/bot)进行apikey的申请）

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

> 请先在`hoshino/config/__bot__.py`的`MODULES_ON`中取消`mikan`的注释  
> 本功能默认关闭，在群内发送 "启用 hourcall" 即可开启

报时功能使用/魔改了艦これ中各个艦娘的报时语音，您可以在[舰娘百科](https://zh.kcwiki.org/wiki/舰娘百科)或[艦これ 攻略 Wiki](https://wikiwiki.jp/kancolle/)找到相应的文本/翻译，当然您也可以自行编写台词。在此，我们向原台词作者[田中](https://bbs.nga.cn/read.php?tid=9143913)[谦介](http://nga.178.com/read.php?tid=14045507)先生和他杰出的游戏作品表达诚挚的感谢！

若您已获取时报文本，在文件`hoshino/config/hourcall.py`中填写您的文本。

您可以编入多组报时文本，机器人会按`HOUR_CALLS_ON`中定义的顺序循环日替。



#### 推特转发

推特转发功能需要推特开发者账号，具体申请方法请自行[Google](http://google.com)。注：现在推特官方大概率拒绝来自中国大陆的新申请，如果您没有境外手机号，您可尝试:
1，账号绑定Gmail或者163邮箱，理论上126也行，注册推特的时间在一周以上，申请时，浏览器语言改成英文、系统时区和居住国家及申请开发者账号时的ip地址保持一致。
2，认真填写申请理由。

若您已有推特开发者账号，在文件`hoshino/config/twitter.py`中填写您的key：

```python
consumer_key = "your_consumer_key",
consumer_secret = "your_consumer_secret",
access_token_key = "your_access_token_key",
access_token_secret = "your_access_token_secret"
```



#### 晴乃词库

舰娘及装备查询功能使用了精简版的晴乃词库，如有需要请加QQ群[Hoshino的后花园](https://jq.qq.com/?wv=1027&k=55fGEgi)或联系晴乃维护组。





## 友情链接

**pcrbot公主连结群聊bot**: https://pcrbot.com/

**干炸里脊资源站**: https://redive.estertion.win/

**公主连结Re: Dive Fan Club - 硬核的竞技场数据分析站**: https://pcrdfans.com/

**yobot**: https://yobot.win/

