# HoshinoPlan：clanbattle

Nonebot会战管理插件开发计划

## 简介

基于nonebot的QQ机器人框架，开发插件`clanbattle`用于群内会战管理。

## 应用背景及需求

本插件运行于nonebot之上，nonebot与酷Q通过CQHttp通信，完成QQ消息的接受与发送。

本插件应支持：

- [x] 单机器人账号管理多个公会
- [x] 多个公会共用一个QQ群：分为一会/二会/三会/...
- [x] 单个QQ号可能拥有多个游戏账号、分属不同公会
- [ ] 对公会使用进行授权
- [ ] 管理公会的增查删改
    - 权限：群主：可修改、删除、查询本公会但不能添加新公会
- [ ] 公会人员的增查删改
    - 权限：群主：均可；本人：仅可对自己进行
- [ ] 报刀报伤害
- [ ] 出刀排队/预约boss
- [ ] 新boss提醒



## 支持命令

SUPERUSER不受权限控制影响

### 公会管理

| 进度 | 命令                 | 参数              | 权限                    | 说明                                                         |
|---| -------------------- | ----------------- | ----------------------- | ------------------------------------------------------------ |
| ok | add-clan             | [--cid] [--name]  | GROUP_OWNER/GROUP_ADMIN | 添加新公会，编号为id，默认为该群最大公会id+1，若无公会则为1；name为公会名 |
| | list-clan            | [--all]           | GROUP_MEMBER            | 默认显示当前QQ群的所有公会；--all 显示管理的所有公会，仅SUPERUSER可用 |
| | mod-clan             | --cid  --new_name | GROUP_OWNER/GROUP_ADMIN | 修改公会的name                                               |
| | del-clan             | --cid             | GROUP_OWNER/GROUP_ADMIN | 删除公会                                                     |
| | ~~set-default-clan~~ | --cid             | GROUP_OWNER             | ~~设置本群的默认公会（缺省值为1）~~                          |

### 成员管理

| 命令                 | 参数                            | 权限            | 说明 |
| -------------------- | ------------------------------- | --------------- | ---- |
| add-member/join-clan | [--cid] --uid --alt --name      | SUPERUSER       |      |
| list-member          | [--cid]                         | SUPERUSER/OWNER |      |
| mod-member           | [--clan] [--uid] [--alt] --name | SUPERUSER/OWNER |      |
| del-member           | [--clan]                        | SUPERUSER/OWNER |      |
|                      |                                 |                 |      |

### Boss信息查询



### 出刀管理

| 命令                | 参数                                | 权限 | 说明                 |
| ------------------- | ----------------------------------- | ---- | -------------------- |
| subscribe           |                                     |      | 预约boss，到达时提醒 |
| add-challenge / dmg | --round --boss --damage --uid --alt |      | 报刀                 |
| mod-dmg             |                                     |      | 改刀                 |
|                     |                                     |      |                      |

### 会战统计

| 命令 | 参数                            | 权限 | 说明             |
| ---- | ------------------------------- | ---- | ---------------- |
| show | [--today] [--all] --uid [--alt] |      |                  |
| plot | [--today] [--all]               |      | 绘制会战分数报表 |
|      |                                 |      |                  |





## 数据储存

### 术语

- gid：QQ群号
- cid：QQ群内下属公会号

- uid：用户的QQ号
- alt：用户的小号编号（默认为0，主账号）
- clan：公会标识，由gid与cid组成`[gid]_[cid]`

```
clanbattle.db
├─clan
├─member
├─subscribe
├─battle_[gid]_[cid]_[yyyymm].csv

```

### config.py

配置boss血量信息、提供简易版作业等

### clan.csv

公会以gid+cid作为唯一标识，name可修改可重复

- gid：qq群号
- cid：该群下的公会号
- name：公会名



### ~~progress.csv~~

~~记录各个公会进度~~ 不再需要，可以根据出刀情况计算

- gid
- cid
- round
- boss

### member.csv

记录成员信息

- uid：qq号
- alt：小号编号
- name：游戏内名字
- gid：所属公会群
- cid：所属公会分会

### subscribe.csv

订阅信息

- sid：订阅编号

- uid：qq号
- alt：小号编号
- gid
- cid
- boss：订阅boss

### battle/[gid]\_[cid]\_[yyyymm].csv

记录出刀信息

- eid：出刀记录编号
- uid：出刀者qq号
- alt：出刀者小号编号
- time：出刀时间`ddhhMMss`
- round：周目数
- boss：Boss编号
- dmg：伤害
- flag：出刀标志 normal/last/extend



## 开发思路

### 一次报刀发生了什么？

首先，获取到dmg命令，提取其中的round、boss、damage/score信息，同时获取报刀者的uid（若给出了alt，则确认其小号）；

然后，根据uid和alt查member表，查出其所属公会的gid和cid；

之后，查询对应的battle记录是否在内存中（若无则载入），录入出刀信息，写入文件；

最后，更新该公会的进度，触发订阅信息。

### 一次统计报表发生了什么？

首先，获取到plot命令，得知gid和cid；

查询对应时间段的battle记录，统计每个账号的出刀记录；

汇总报表（并绘图），输出；

### 分层设计

- 命令层 - `__init__.py`中的各种命令：接受机器人指令并调用服务层处理
- 服务层 - BattleMaster：将数据层的基本操作组合，形成服务
- 数据层 - DAOs：直接与SQLite交互，支持基本的增查删改



## 心得

- 学习了SQLite的使用（增查删改/CRUD）
- 实践了一下DAO的设计模式；但由于本项目并没有那么庞大，而且Python语言十分便利，并没有完全按照Java的面向接口开发模式来操作，不过以后如果需要改用别的数据库，只需要增加一个dao/xxxdao.py，修改battlemaster的import语句即可。

- 学习了python的命令行参数处理工具 [Argparse](https://docs.python.org/zh-cn/3.6/howto/argparse.html) 